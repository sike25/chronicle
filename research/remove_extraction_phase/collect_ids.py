"""
collect_ids.py

Runs each experiment query through Vertex Search and collects the returned document IDs.
Saves a JSON file with per-query ID lists and a deduplicated union for use in precompute_summaries.py.

"""

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from modules.fetch import fetch_search_results
from utils.log     import setup_logging

logger = setup_logging()

QUERIES = ["Jay-Jay Okocha", "Women in politics", "Nollywood", "Biafran War"]
OUTPUT_PATH = "collected_ids.json"


def collect_ids(queries):

    per_query = {}

    for query in queries:
        logger.info(f"Fetching results for query: {query}.")
        try: 
            ids = []
            search_results = fetch_search_results(query, fake=False)
            for result in search_results:
                ids.append(result.document.id)
            per_query[query] = ids
            logger.info(f"    -> Collected {len(ids)} results.")
        except Exception as e:
            logger.error(f"CHRONICLE_RESEARCH_ERROR: Error fetching search results for {query}: {e}.")

    all_ids = list({id for ids in per_query.values() for id in ids})
    logger.info(f"Total unique IDs across all queries: {len(all_ids)}")
 
    return {
        "queries":      per_query,
        "all_ids":      all_ids,
    }


data = collect_ids(QUERIES)
with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
logger.info(f"Saved to {OUTPUT_PATH}")


