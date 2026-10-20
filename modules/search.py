import os
import time
from urllib.parse import quote

import requests
from google.cloud import discoveryengine_v1 as de

from utils.log import setup_logging

logger = setup_logging()


ARCHIVE_API_PREFIX = "v1"

PER_PAGE      = 100
MAX_DOCUMENTS = 500
MAX_RETRIES   = 3

# The Vertex AI ranking API accepts at most 200 records per request.
RANK_BATCH_SIZE = 200

PROJECT_ID     = "chronicle-archiving"
RANKING_CONFIG = "default_ranking_config"
RANKING_MODEL  = "semantic-ranker-default-004"


def _base_api_url() -> str:
    url = os.environ.get("ARCHIVI_API_URL", "").strip().rstrip("/")
    if not url:
        raise RuntimeError("ARCHIVI_API_URL environment variable is not set.")
    return url


def search(query: str, start_date: str = None, end_date: str = None, publication: str = None) -> list:
    """
    Searches archivi.ng, reranks the hits against the query, and returns them oldest first.

    Args:
        query       (str): The search query.
        start_date  (str): Optional, "YYYY-MM-DD".
        end_date    (str): Optional, "YYYY-MM-DD".
        publication (str): Optional publication filter.

    Returns:
        list[dict]: archivi.ng result objects sorted by ascending date, each with an added
                    "relevance_score" (0-1) from the reranker.
    """
    results = _fetch_from_archivi(query, start_date, end_date, publication)
    logger.info(f"new_search: fetched {len(results)} results from archivi.ng.")
    if not results:
        return []

    results = _rerank(query, results)
    results.sort(key=lambda r: r["date"])
    return results


def _fetch_from_archivi(query, start_date, end_date, publication) -> list:
    params = {
        "extract":  query,
        "per_page": PER_PAGE,
        "sort_by":  "relevance",
        "page":     1,
    }
    if start_date:  params["start_date"]  = start_date
    if end_date:    params["end_date"]    = end_date
    if publication: params["publication"] = publication

    results = []
    while len(results) < MAX_DOCUMENTS:
        resp = requests.get(f"{_base_api_url()}/{ARCHIVE_API_PREFIX}/search", params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        results.extend(data["body"])

        total_pages = data["pagination"].get("total_pages", 1)
        if not data["body"] or params["page"] >= total_pages:
            break
        params["page"] += 1

    return results[:MAX_DOCUMENTS]



def fetch_transcript(page_id: str):
    """
    Fetches a page's OCR transcript from archivi.ng.

    Returns the text, or None if the page has no transcript available.
    Raises if the request still fails after MAX_RETRIES attempts.
    """
    url = f"{_base_api_url()}/{ARCHIVE_API_PREFIX}/page/{quote(page_id, safe='')}/transcript"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=60)
            if resp.status_code == 404:
                return None
            if resp.status_code < 500:
                resp.raise_for_status()
                body = resp.json()["body"]
                return (body.get("text") if body.get("status") == "available" else None) or None
            error = f"HTTP {resp.status_code}"
        except (requests.RequestException, KeyError, ValueError) as e:
            error = str(e)
        if attempt < MAX_RETRIES:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Transcript fetch for page {page_id} failed after {MAX_RETRIES} attempts: {error}")


def _required(result: dict, field: str) -> str:
    value = result.get(field)
    if not value or not str(value).strip():
        raise ValueError(f"archivi.ng result {result.get('id')!r} is missing required field '{field}'.")
    return value


def _rerank(query: str, results: list) -> list:
    client = de.RankServiceClient()
    config = client.ranking_config_path(
        project=PROJECT_ID, location="global", ranking_config=RANKING_CONFIG
    )

    # Records are keyed by index into `results`; ids need only be unique within a request,
    # but a global index keeps the mapping trivial across batches.
    for start in range(0, len(results), RANK_BATCH_SIZE):
        batch = results[start:start + RANK_BATCH_SIZE]
        records = [
            de.RankingRecord(
                id=str(start + i),
                title=f"{_required(r, 'publication')} {_required(r, 'date')}",
                content=_required(r, "summary"),
            )
            for i, r in enumerate(batch)
        ]
        resp = client.rank(request=de.RankRequest(
            ranking_config=config,
            model=RANKING_MODEL,
            query=query,
            records=records,
            top_n=len(records),
        ))
        for record in resp.records:
            results[int(record.id)]["relevance_score"] = record.score

    return results
