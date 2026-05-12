# Extraction Phase Experiment

## Background

Chronicle's enrichment pipeline runs in two phases. 
Phase 1 (extraction) takes each document returned by search and uses an LLM to distill the portions most relevant to the user's query. 
Phase 2 (enrichment) synthesizes those extracts into cluster titles and summaries.

Phase 1 exists because newspaper pages carry multiple stories, and passing full pages
into Phase 2 would flood the context with noise, inflate costs, and slow the pipeline.

But Phase 1 is the slowest part of Chronicle and adds an additional $1.50 per query, on average.
Hence, we want to consider the possibility of removing Phase 1.

Each document in the archive carries two pre-generated text fields:
- `extract` — a raw OCR excerpt, often noisy and not query-aware
- `summary` — a pre-generated summary of the document's contents, not query-specific

Phase 1 is currently based on the raw OCR  `extract`. 



## Research Question

How do the cost and quality results compare between these options?
1. Query-specific, on-the-fly extraction (current implementation, phase 1).
2. Query-agnostic, pre-generated, non-detailed summaries (current `summary` field).
3. Query-agnostic, pre-generated, richer, detailed summaries (improvement on current `summary` field).


## Queries Under Test

1. **Jay-Jay Okocha** — proper noun with a clear, specific referent
2. **Women in politics** — thematic and abstract; tests loose relevance judgement
3. **Nollywood and the film industry** — domain query with broad coverage
4. **Biafran War**— historically dense


## Quality Evaluation Rubric

Each condition's output is scored per query across these dimensions:

- **Completeness**  — are the important events and entities present in the timeline?
- **Specificity**   — are titles and summaries precise, or generic?
- **Coherence**     — does each cluster read as a unified narrative?
- **Noise**         — is irrelevant content leaking into the output?
- **Hallucination** — does the output introduce claims not supported by the sources?

Scored per cluster (1–3), averaged across the timeline.


## Other Metric

Beyond output quality, record per condition:

- Total token usage (Phase 1 + Phase 2)
- End-to-end latency

A quality win for condition 1 that costs 3× the tokens may not be worth it at scale.
The goal is to find the best quality-to-cost ratio, not the best quality in isolation.


## Expected Outcome

Condition 1 likely performs best on abstract and ambiguous queries where noise removal
matters most. Condition 2 may be competitive if the detailed summaries are rich enough.
Condition 3 is the baseline — the floor everything else should beat.

If condition 2 comes close to condition 1, the case for making Phase 1 optional
(behind a flag) becomes strong.