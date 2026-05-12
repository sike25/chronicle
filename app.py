import json
import threading
import uuid

from datetime                import datetime
from fastapi                 import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses       import StreamingResponse
from pydantic                import BaseModel, field_validator

from pipeline    import run_chronicle
from utils.cache import cache
from utils.jobs  import jobs
from utils.log   import setup_logging

logger = setup_logging()


# set up app
app = FastAPI(
    title="Chronicle",
    description="Transforms archivi.ng search results into an enriched, chronological timeline.",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://archivi.ng", "https://proto-chronicle.streamlit.app"],
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# input schema
class ChronicleRequest(BaseModel):
    query:      str
    start_date: str  = ""
    end_date:   str  = ""
    no_cache:   bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [{"query": "Election crises and violence", "start_date": "2014-01-01", "end_date": "2023-12-31"}]
        }
    }

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date(cls, v):
        if not v:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

# routes
@app.post("/chronicle", status_code=202)
def start_chronicle(request: ChronicleRequest):
    """
    Accepts a search query and kicks off the Chronicle pipeline in the background.
    Returns a job_id immediately. Use GET /chronicle/{job_id}/stream to consume results.
    """

    job_id = str(uuid.uuid4())
    jobs.create(job_id)
    logger.info(f"Job created: {job_id} for query: '{request.query}")

    # try reading results from cache
    if not request.no_cache:
        cached_events = cache.get(request.query, request.start_date, request.end_date)
        if cached_events:
            logger.info(f"Cache HIT — replaying into job {job_id}")
            _replay_cached_events(job_id, cached_events)
            return {"job_id": job_id}

    # run chronicle afresh
    logger.info(f"Cache MISS — running fresh for job {job_id}")
    thread = threading.Thread(
        target=_run,
        args=(job_id, request),
        daemon=True,
    )
    thread.start()

    return {"job_id": job_id}


@app.get("/chronicle/{job_id}/stream")
def stream_chronicle(job_id: str):
    """
    See stream for a Chronicle job.

    Events emitted in order:
    - clusters_ready    = pipeline has clustered results; includes cluster counts and date labels
    - clusters_enriched = one enriched cluster is ready to render
    - done              = all clusters have been emitted
    - error             = something went wrong; details included.
    """
    if not jobs.exists(job_id):
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    
    return StreamingResponse(
        _event_stream(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

@app.get("/health")
def health():
    return {"status": "ok"}



def _replay_cached_events(job_id: str, events: list):
    """Push cached events directly into job store so that SSE stream replays them."""
    for event in events:
        jobs.push_event(job_id, event["type"], event["data"])
    logger.info(f"Cache: replayed {len(events)} events into job {job_id}")


# pipeline runner
def _run(job_id:str, request: ChronicleRequest):
    """Runs the Chronicle pipeline and writes results to the job store."""
    try:
        run_chronicle(query=request.query, job_id=job_id)

        # write fresh results into cache
        if not request.no_cache:
            events = jobs.get_events(job_id)
            cache.set(request.query, events, request.start_date, request.end_date)

    except Exception as e:
        logger.error(f"CHRONICLE_ERROR: Pipeline failure for job {job_id}: {e}")
        jobs.set_error(job_id, str(e))

# sse event stream
def _event_stream(job_id: str):
    """
    Generator that yields SSE-formatted events from the job store.
    Blocks until new events are available, then yields them one by one.
    """

    cursor = 0
    while True:
        status = jobs.get_status(job_id)
        events = jobs.get_events(job_id)

        # yield new events since our cursor
        while cursor < len(events):
            event = events[cursor]
            yield _format_sse(event["type"], event["data"])
            cursor += 1

        if status in ["done", "error"]: break

        # small sleep to avoid spinning while pipeline is running
        threading.Event().wait(timeout=1)

def _format_sse(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
