# prepare.py

def preprocess(results):
    return sort_by_date(results)

def hard_filter(results, threshold=0.6):
    '''Shave off any results with semantic relevance scores below a given threshold.'''
    if not results:
        return []
    return [res for res in results if res.semantic_relevance >= threshold]

def sort_by_date(results):
    results.sort(key=lambda x: x.source.publication_date.to_python_datetime())
    return results