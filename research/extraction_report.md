## REPORT

### Original (Extractive)

    system_prompt = "You are a research assistant. Extract only text directly relevant to the user's query. " \
    "If no relevance exists, return 'No relevant data'."
    
    user_content = f"""Query: {query}
    Document: {entry.source.filename}
    Text: {entry.source.extract}
    
    Task: Extract the exact sentences or paragraphs from the Text that discuss "{query}". 
    Include dates, names, and specific events. Do not summarize; extract original text."""


Pulls direct quotes formatted as numbered items with bold headers. Good for citation, but reads as fragments rather than prose.
Tends to miss peripheral but relevant items — e.g. actress personal/legal news (#116: Eucharia divorce).
Consistently fails when query terms don’t appear verbatim, even when content is directly relevant (#66, #76).
Narrows further on sparse content — when the source is just photo captions, it dropped one of two equally minimal entries with no apparent reason (#30: included Babangida, dropped Hashidu).
Handles truncated source text honestly — flags where content cuts off rather than silently dropping or completing it (#48: “[text cuts off]”).
When it works, adds useful parenthetical context to situate quotes (e.g. #169: attributing speaker, explaining antecedents).


### Subtractive

    system_prompt = "You are a research assistant going through extracts from historical African newspapers."
    
    user_content = f"""Query: {query}
    Document: {entry.source.filename}
    Text: {entry.source.extract}
    
    Task: Remove parts of the Text that have nothing to do with the search query: "{query}" and return the rest word for word. 
    If nothing in the Text is relevant, remove it all and return 'No relevant data'.
    """

Reconstructs the article as flowing prose, stripping content unrelated to the query. Most readable of the three.
Inconsistent aggressiveness: can drop clearly relevant items (#116: Eucharia divorce) but also retain clearly irrelevant ones (#66: personal questions about womanizing and marriage).
Also narrows on sparse content without justification — dropped Hashidu from the caption extract for no clear reason (#30), same behaviour as Original.
OCR noise handling is inconsistent — cleaned artifacts in some examples but passed them through verbatim in others (#169, #89).


### Summary

    system_prompt = "You are a research assistant going through extracts from historical African newspapers."
    
    user_content = f"""Query: {query}
    Document: {entry.source.filename}
    Text: {entry.source.extract}
    
    Task: Summarize the information in the Text that is either directly or loosely related to the search query: "{query}".
    Be throrough about including all specific details and context, including dates, numbers, names, selected quotes, and specific events.
    If nothing in the Text is relevant to the query, return 'No relevant data'.
    """


Structured bullet-point synthesis with named entities and grouped topics. Best for quick scanning.
Most consistently complete and accurate of the three across all examples.
Handles OCR damage gracefully — brackets unclear passages rather than reproducing garbled text or silently dropping them (#89: “[something related to]”).
Good at connecting contextual details back to the query topic — linked Uganda’s 7% growth rate and $820m aid figures to the SAP as outcomes, which Original and Subtractive didn’t do (#48).
Inferential tendency cuts both ways: on sparse content it expands usefully (#30: added Hashidu’s role in the Babangida administration), but it also silently completes truncated source text rather than flagging it (#48: completed “all-embrac-” as “all-embracing” without noting the cut-off). Likely correct, but worth monitoring.
Remaining blind spot: illustrative anecdotes and parables, even when doing argumentative work. Captures conclusions but drops the reasoning behind them (#corruption: Adeboye’s David and Bathsheba parable).


### General
None of the methods attempt disambiguation when a query term matches unexpectedly — a search for “babangida” returned content about footballer Tijani Babangida without flagging that the likely intended subject was Ibrahim Babangida (#89).
All three correctly ignored unrelated stories within multi-article pages (#169: court cases, customs transfer).
OCR noise cleaning appears inconsistent across methods and examples — worth investigating whether it’s intentional.