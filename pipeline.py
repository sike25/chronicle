from modules.cluster import cluster_by_stride
from modules.shape   import Source, Entry
from modules.enrich  import enrich_clusters
from modules.filter  import hard_filter
from modules.fetch   import fetch_search_results
from utils.helpers   import convertToDate
from utils.jobs       import jobs
from utils.log       import setup_logging

logger = setup_logging()

def run_chronicle(query: str, job_id: str):
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
            search_results = fetch_search_results(query=query, fake=True)
        except Exception as e:
            logger.error(f"CHRONICLE_ERROR: Error fetching search results for {query}: {e}.")
            if not search_results: raise

        entries = []
        for result in search_results:
            try:   
                source = Source(
                    summary           = result.document.struct_data["summary"],
                    extract           = result.document.struct_data["extract"],
                    filename          = result.document.struct_data["filename"],
                    keywords          = result.document.struct_data["keywords"].split(","),
                    image_path        = result.document.struct_data["image_path"],
                    topics            = result.document.struct_data["topics"].split(","),
                    publication       = result.document.struct_data["publication"],
                    publication_date  = convertToDate(result.document.struct_data["publication_date"]),
                    page              = result.document.struct_data["page"],
                    tags              = result.document.struct_data["tags"].split(","),
                )
                entry = Entry(
                    id     = result.document.id,
                    source = source,
                    semantic_relevance = result.rank_signals.semantic_similarity_score,
                )
                entries.append(entry)
            except Exception as e:
                logger.error(f"CHRONICLE_ERROR: Mapping error for doc {result.document.id}: {e}")

        logger.info("Done!")
        logger.info(f"Retrieved {len(entries)} raw results.")

        # 2. FILTER
        # Ultimately, search results are filtered by:
        # - hard limit on the total allowed number of results.
        # - hard limit on relevance score
        # - keeping documents above the mean or median relevance
        logger.info("FILTER ---------------------------------------------------------------")
        entries = hard_filter(results=entries)
        logger.info(f"After filtering: {len(entries)} results.")

        if not entries:
            jobs.push_event(job_id, "error", {"message": "No relevant results found for this query."})
            return

        # 3. SORT
        # Sort chronologically. In the future, combine with filtering logic into a prepare.py file.
        logger.info("SORT -----------------------------------------------------------------")
        entries.sort(key=lambda x: x.source.publication_date.to_python_datetime())

        # 4. CLUSTER
        logger.info("CLUSTER --------------------------------------------------------------")
        clusters = cluster_by_stride(entries=entries)
        logger.info(f"{len(clusters)} clusters formed.")

        # emit clusters_ready so the frontend can render skeletons immediately
        jobs.push_event(job_id, "clusters_ready", {
            "cluster_count": len(clusters),
            "labels": list(clusters.keys()),
        })

        # 5. ENRICH
        logger.info("ENRICH ---------------------------------------------------------------")
        enriched_clusters = enrich_clusters(clusters=clusters, query=query, job_id=job_id)
        logger.info(f"RUN COMPLETE | job={job_id}")

        logger.info("FINAL RESULTS ---------------------------------------------------------------")
        logger.info("Enriched Clusters:")
        if enriched_clusters:
            for _, enriched_cluster in enriched_clusters.items():
                logger.info("\n")
                logger.info(f"--> Enriched Cluster {enriched_cluster.label}:")
                logger.info(f"------> Titled `{enriched_cluster.title}`")
                logger.info(f"------> Summary: {enriched_cluster.summary}")
                logger.info(f"------> Compiled from {len(enriched_cluster.entries)} sources")
            return enriched_clusters
    except Exception as e:
        logger.error(f"CHRONICLE_ERROR: Pipeline failure. {e}")
        raise

# run_chronicle_pipeline()