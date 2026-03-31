from utils.log      import setup_logging
from modules.search import search_data_dump
from modules.fake   import fake_search_results

logger = setup_logging()


# Page size for paginating archivi.ng's search API.
PAGE_SIZE = 100
# Hard cap on total documents regardless of signal.
MAX_DOCUMENTS = 500

def fetch_search_results(query: str, fake=True) -> list:
    """
    Fetches search results from archivi.ng's search API.

    Paginates through results, stopping when:
        - Fewer than SIGNAL_THRESHOLD of a page passes the relevance filter, OR
        - MAX_DOCUMENTS total documents have been collected.

    Args:
        query (str): The search query.
        fake  (bool): If True, returns fake data for local development.

    Returns:
        list: Raw result objects ready to be mapped into Entry shapes in pipeline.py.
    """
    if fake:
        logger.info("fetch_results: returning fake data.")
        return fake_search_results()

    logger.info(f"fetch_results: fetching live results for query '{query}'.")
    return _fetch_from_vertex(query=query)


def _fetch_from_vertex(query: str):
    collected = []
    pager = search_data_dump(search_query=query)

    for result in pager:
        if len(collected) >= MAX_DOCUMENTS or result.rank_signals.semantic_similarity_score == 0.0:
            break
        collected.append(result)
    return collected


# ── Live fetcher ──────────────────────────────────────────────────────────────
def _fetch_live(query: str) -> list:
    """
    Paginates through archivi.ng's search API until signal dries up.

    TODO: implement once archivi.ng's search API spec is available.
          Expected pagination params: ?q=query&from=0&size=20
          Expected response shape:
            {
              "total": 1200,
              "hits": [
                {
                  "_id": "...",
                  "_score": 0.87,
                  "_source": { ... }
                }
              ]
            }
    """
    raise NotImplementedError(
        "Live fetcher not yet implemented. "
        "Waiting on archivi.ng search API spec. Use fake=True for local development."
    )

    # stub for when the spec arrives ........................................
    # import requests
    #
    # SEARCH_API_URL = "https://archivi.ng/api/search"
    # all_results = []
    # page = 0
    #
    # while len(all_results) < MAX_DOCUMENTS:
    #     response = requests.get(SEARCH_API_URL, params={
    #         "q":    query,
    #         "from": page * PAGE_SIZE,
    #         "size": PAGE_SIZE,
    #     })
    #     response.raise_for_status()
    #     data = response.json()
    #     hits = data.get("hits", [])
    #
    #     if not hits:
    #         logger.info("fetch: no more results. Stopping.")
    #         break
    #
    #     # check signal — how many hits on this page pass the relevance threshold
    #     passing = [h for h in hits if h["_score"] >= 0.6]
    #     signal  = len(passing) / len(hits)
    #     logger.debug(f"fetch: page {page} — {len(passing)}/{len(hits)} hits pass filter (signal={signal:.2f})")
    #
    #     all_results.extend(hits)
    #
    #     if signal < SIGNAL_THRESHOLD:
    #         logger.info(f"fetch: signal dropped below {SIGNAL_THRESHOLD}. Stopping.")
    #         break
    #
    #     page += 1
    #
    # logger.info(f"fetch: collected {len(all_results)} results across {page + 1} pages.")
    # return all_results
