import anthropic
import concurrent.futures
import random
from modules.shape import EnrichedCluster
from utils.helpers import extractJson
from utils.jobs    import jobs
from utils.log     import setup_logging

DUMB_MODEL  = "claude-haiku-4-5"
SMART_MODEL = "claude-sonnet-4-5"

logger = setup_logging()
client = anthropic.Anthropic()

def enrich_clusters(clusters, query, job_id):
    """
    Enriches newspaper clusters with cohesive context (title, summary, cover story).

    Two-phase approach:
        Phase 1 (parallel):   All Haiku extraction calls across all clusters fire
                              simultaneously in a single ThreadPoolExecutor.
        Phase 2 (sequential): Sonnet synthesis runs in chronological order, feeding
                              global_context_history forward to prevent duplicate titles.

    Pushes SSE events to the job store as each cluster is enriched.

    Args:
        clusters (dict): Dictionary of {date_range: [Entry, ...]} in chronological order.
        query    (str):  The original search string.
        job_id   (str):  The job ID for pushing SSE events.
    """

    # Trim large clusters to top 20 in semantic relevance.
    # TODO (ogieva): This is a heuristic. In the future, we implement hierarchical extraction.
    trimmed_clusters = trim_large_clusters(clusters=clusters)

    # Phase 1: Parallel Extraction.
    # Files are sent to a dumb model to extract the portions which are relevant to the query.
    # This is because newspaper pages often carry more than one story, 
    # and we want to minimize expensive API calls from large inputs.
    # TODO (ogieva): This might be replaced with search functionality, if it exists.
    logger.info(f"Phase 1: parallel extraction across {len(trimmed_clusters)} clusters...")
    all_entries = [
        entry
        for entries in trimmed_clusters.values()
        for entry in entries
    ]
    run_parallel_extraction(all_entries, query)
    logger.info("Phase 1 complete.")

    # Phase 2: Sequential enrichment
    # Runs in chronological order so history can be fed forward.
    # This avoids repetitive, non-specific titles and summaries
    logger.info("Phase 2: enrich clusters sequentially.")
    enriched = run_sequential_enrichment(trimmed_clusters, query, job_id)
    logger.info("Phase 2 complete. All clusters enriched.")
    return enriched

 
def run_parallel_extraction(all_entries, query):
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_entry = {
            executor.submit(extract_relevant_portions, entry, query): entry
            for entry in all_entries
        }
        for future in concurrent.futures.as_completed(future_to_entry):
            entry = future_to_entry[future]
            try:
                entry.source.relevant_extract = future.result()
            except Exception as e:
                logger.error(f"Extraction failed for {entry.source.filename}: {e}. Falling back to full extract.")
                entry.source.relevant_extract = f"Extract: {entry.source.extract}"

    
def extract_relevant_portions(entry, query):
    """
    Uses a fast, dumb model (Haiku) to extract only query-relevant text.
    No JSON requirement here to increase speed and reliability.
    """
    
    system_prompt = "You are a research assistant. Extract only text directly relevant to the user's query. " \
    "If no relevance exists, return 'No relevant data'."
    
    user_content = f"""Query: {query}
    Document: {entry.source.filename}
    Text: {entry.source.extract}
    
    Task: Extract the exact sentences or paragraphs from the Text that discuss "{query}". 
    Include dates, names, and specific events. Do not summarize; extract original text."""

    try:
        response = client.messages.create(
            model=DUMB_MODEL,
            max_tokens=1000,
            temperature=0,   # deterministic for extraction
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}]
        )
        
        extracted_text = response.content[0].text.strip()
        if not extracted_text or "No relevant data" in extracted_text:
            logger.warning(f"No relevant data extracted from {entry.source.filename}")
            return f"Extract: {entry.source.extract}"
        return extracted_text
        
    except Exception as e:
        logger.error(f"CHRONICLE_ERROR: Error extracting from {entry.source.filename}: {e}")
        raise
    

def run_sequential_enrichment(trimmed_clusters, query, job_id):
    global_context_history = []
    enriched_clusters = {}

    for index, (label, entries) in enumerate(trimmed_clusters.items()):

        logger.info(f"Enriching cluster {index}: '{label}'...")
        title, summary = generate_bucket_context(
            query=query,
            entries=entries,
            dates=label,
            history=global_context_history,
        )
        global_context_history.append({"date": label, "title": title, "summary": summary})

        enriched = EnrichedCluster(
            index       = index,
            label       = label,
            title       = title,
            summary     = summary,
            entries     = entries,
            start_date  = entries[0].source.publication_date,
            end_date    = entries[-1].source.publication_date,
            cover_story = select_cover_story(entries)
        )

        enriched_clusters[label] = enriched
        jobs.push_event(job_id, "cluster_enriched", enriched.to_dict())
        logger.info(f"Cluster {index} enriched: '{title}'")

    jobs.push_event(job_id, "done", {})
    return enriched_clusters


def generate_bucket_context(query, entries, dates, history=None):
    # format the history into a string to supply llm to avoid repetitive titles and summaries.
    history_text = "NONE (This is the first cluster)"
    if history:
        history_text = "\n".join([
            f"- {h['date']}: {h['title']}" for h in history[-3:] # Last 3 are usually enough
        ])

    entries_text = "".join([f"Source {i}: {e.source.relevant_extract}\n---\n" for i, e in enumerate(entries[:15])])

    context_generation_prompt = f"""You are a news historian synthesizing clusters of Nigerian newspaper archives.

    GLOBAL CONTEXT:
    Previous clusters in this timeline were titled:
    {history_text}

    CURRENT TASK:
    Analyze the {len(entries)} articles from {dates} regarding "{query}".
    
    REQUIREMENTS:
    1. TITLE: Must be distinct from previous titles. Focus on the *specific* event or shift in this period.
    2. SUMMARY: A cohesive paragraph explaining what happened *new* in this window compared to the past.

    NEW ARTICLES FOR {dates}:
    {entries_text}

    Return ONLY valid JSON:
    {{
        "title": "Distinct, specific title",
        "summary": "Synthesized summary"
    }}"""
    
    try:
        response = client.messages.create(
            model=SMART_MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": context_generation_prompt}]
        )
        result = extractJson(response.content[0].text)

        if result:
            return result.get('title'), result.get('summary')
        else:
            raise KeyError(f"CHRONICLE: Missing required fields in response -> {response}")
     
    except Exception as e:
        logger.error(f"CHRONICLE_ERROR: Context generation failed: {e}")
        return f"Results for '{query}'", f"Collection of {len(entries)} articles from {dates} related to {query}."
    

def select_cover_story(entries):
    # Select the story with the highest relevance score as the cover story.
    # TODO (ogieva): In the future, we will tokenize each entry and the LLM-generated title.
    # The story which most closely relates to the generated title will be the cover story.
    return max(entries, key=lambda e: e.semantic_relevance)
    

def trim_large_clusters(clusters):
    # Trim large clusters to top 20 in semantic relevance.
    # TODO (ogieva): This is a heuristic. In the future, we implement hierarchical extraction.
    trimmed_clusters = {}
    for label, entries in clusters.items():
        if len(entries) > 20:
            logger.info(f"Large cluster ({len(entries)} entries) at '{label}'. Trimming to top 20.")
            entries = sorted(entries, key=lambda e: e.semantic_relevance, reverse=True)[:20]
        trimmed_clusters[label] = entries
    return trimmed_clusters
    
