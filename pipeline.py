
from modules.shape   import Source, Entry
from modules.search  import search
from modules.cluster import cluster_into_buckets
from modules.enrich  import enrich_clusters

from utils.helpers   import convertToDate
from utils.jobs      import jobs
from utils.log       import setup_logging

import uuid

logger = setup_logging()

def run_chronicle(query: str, job_id: str, start_date:str, end_date:str, publication:str):
    """
    Coordinates the full flow of the Chronicle feature, from fetching search results to cluster enrichment.

    Fetch and Filter -> Sort -> Cluster -> Enrich
        1. Fetch   — paginate archivi.ng search results until signal dries up
        2. Filter   — drop low-relevance results
        3. Sort     — chronological order
        4. Cluster  — group into semantic time-ordered buckets
        5. Enrich   — two-phase: extraction of relevant document excerpts, then enriching clusters with context.
    """

    try:
        logger.info(f"RUN STARTED | job={job_id} | query='{query}'")

        # 1. FETCH 
        # Fetch search results from the archivi.NG search API page by page until the signal 
        # (indicated by semantic relevance score) dries up, 
        # or the hard limit on total search results is met.
        logger.info("FETCH  ---------------------------------------------------------------")
        search_results = None
        try:
            search_results = search(query, start_date, end_date, publication)
        except Exception as e:
            logger.error(f"CHRONICLE_ERROR: Error fetching search results for {query}: {e}.")
            if not search_results: raise

        entries = []
        for result in search_results:
            try:
                source = Source(
                    summary          = result["summary"],
                    extract          = result["match_excerpt"],   # see point 3
                    filename         = result["slug"],            # no filename in the new API
                    keywords         = [k.strip() for k in result["keywords"].split(",")],
                    image_path       = result["image_path"],
                    topics           = [t.strip() for t in result["topics"].split(",")],
                    publication      = result["publication"],
                    publication_date = convertToDate(result["date"]),   # "1994/07/01"
                    page             = result["page"],
                )
                entries.append(Entry(id=result["id"], source=source,
                                    semantic_relevance=result["relevance_score"]))
            except Exception as e:
                logger.error(f"... Mapping error for doc {result.get('id')}: {e}")


        logger.info("Done!")
        logger.info(f"Retrieved {len(entries)} raw results.")
        if not entries:
            jobs.push_event(job_id, "done", {"message": "No relevant results found for this query."})
            return

        # 2. CLUSTER
        logger.info("CLUSTER --------------------------------------------------------------")
        clusters = cluster_into_buckets(entries=entries)
        logger.info(f"{len(clusters)} clusters formed.")

        # log prepared clusters.
        log_clusters = f""
        for i, (date, entries) in enumerate(clusters.items()):
            log_clusters += f"{i}: {date} — {len(entries)} entries.\n"
        logger.info(log_clusters)

        # emit clusters_ready so the frontend can render skeletons immediately
        jobs.push_event(job_id, "clusters_ready", {
            "cluster_count": len(clusters),
            "labels": list(clusters.keys()),
        })

        # 3. ENRICH
        logger.info("ENRICH ---------------------------------------------------------------")
        enriched_clusters = enrich_clusters(clusters=clusters, query=query, job_id=job_id, fake=False)
        logger.info(f"RUN COMPLETE | job={job_id}")

        # log final results - enriched clusters.
        logger.info("FINAL RESULTS ---------------------------------------------------------------")
        log_enriched_clusters = f""
        if enriched_clusters:
            for _, enriched_cluster in enriched_clusters.items():
                log_enriched_clusters += "\n"
                log_enriched_clusters += f"--> Enriched Cluster {enriched_cluster.label}:\n"
                log_enriched_clusters += f"------> Titled `{enriched_cluster.title}`\n"
                log_enriched_clusters += f"------> Summary: {enriched_cluster.summary}\n"
                log_enriched_clusters += f"------> Compiled from {len(enriched_cluster.entries)} sources.\n"
            logger.info(log_enriched_clusters)
            return enriched_clusters
    except Exception as e:
        logger.error(f"CHRONICLE_ERROR: Pipeline failure. {e}")
        raise


# job_id = str(uuid.uuid4())
# jobs.create(job_id)
# run_chronicle("jay jay okocha", job_id, "", "", "TELL")
