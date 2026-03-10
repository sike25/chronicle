import threading
from utils.log import setup_logging

logger = setup_logging()


class JobStore:
    """
    In-memory store for Chronicle pipeline jobs.

    Each jon holds a status and an ordered list of SSE events.
    The main pipeline writes to the store via push_event().
    The SSE stream in app.py reads from it via get_events().

    This is designed to be swapped out for Redis later without changing the API surface.
    """

    # valid statuses
    PENDING  = "pending"   # job created, pipeline not yet started
    RUNNING  = "running"   # pipeline is active
    DONE     = "done"      # pipeline completed successfully
    ERROR    = "error"     # pipeline failed

    def __init__(self):
        self._store: dict = {}
        self._lock = threading.Lock()

    # write API (called by pipeline.py)
    def create(self, job_id: str):
        """
        Initialise a new job. Called immediately when POST /chronicle is received.
        """
        with self._lock:
            self._store[job_id] = {
                "status": self.PENDING,
                "events": [],
            }
        logger.info(f"Job store: created job {job_id}")

    def push_event(self, job_id: str, event_type: str, data: dict):
        """
        Append an SSE event to the job's event list.
        Called by the pipeline as each stage completes.

        event_type is one of: clusters_ready | cluster_enriched | done | error
        """
        with self._lock:
            if job_id not in self._store:
                logger.warning(f"Job store: push_event called on unknown job {job_id}")
                return

            # transition status on meaningful events
            if event_type == "clusters_ready":
                self._store[job_id]["status"] = self.RUNNING
            elif event_type == "done":
                self._store[job_id]["status"] = self.DONE
            elif event_type == "error":
                self._store[job_id]["status"] = self.ERROR

            # append event to job
            self._store[job_id]["events"].append({
                "type": event_type,
                "data": data,
            })

            logger.debug(f"Job store: pushed '{event_type}' event to job {job_id}")

    def set_error(self, job_id: str, message: str):
        """
        Push an error event and mark the job as failed.
        """
        self.push_event(job_id, "error", {"message": message})

    
    # read API (called by app.py)
    def exists(self, job_id: str) -> bool:
        with self._lock:
            return job_id in self._store
        
    def get_status(self, job_id: str) -> str | None:
        with self._lock:
            job = self._store.get(job_id)
            if job:
                return job["status"]
        logger.warning(f"Job Store: get_status called on unknown job {job_id}")
        return None

    def get_events(self, job_id: str) -> list:
        """
        Returns a snapshot of the event list.
        The SSE stream uses a cursor against this list to yield only new events.
        """
        with self._lock:
            job = self._store.get(job_id)
            if job:
                return list(job["events"])
        logger.warning(f"Job Store: get_events called on unknown job {job_id}")
        return []

# global instance — imported by both app.py and pipeline.py
jobs = JobStore()





