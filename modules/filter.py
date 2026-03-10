# filter.py

def hard_filter(results, threshold=0.6):
    '''Shave off any results with semantic relevance scores below a given threshold.'''
    if not results:
        return []
    return [res for res in results if res.semantic_relevance >= threshold]