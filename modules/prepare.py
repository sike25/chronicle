# prepare.py

from utils.helpers import convertToDate

def preprocess(results, start_date, end_date):

    return sort_by_date(filter_by_date(results, start_date, end_date))

def hard_filter(results, threshold=0.6):
    '''Shave off any results with semantic relevance scores below a given threshold.'''
    if not results:
        return []
    return [res for res in results if res.semantic_relevance >= threshold]


def filter_by_date(results, start_date, end_date):
    """Drop entries that fall outside the requested date window.
    Bounds are inclusive. Missing bound means open-ended."""
    if not start_date and not end_date:
        return results
    
    # convert dates from string to Date
    if start_date:
        start_date = convertToDate(start_date)
    if end_date:
        end_date   = convertToDate(end_date)
    
    filtered = []
    for entry in results:
        pub_date = entry.source.publication_date
        if start_date and pub_date < start_date:
            continue
        if end_date and pub_date > end_date:
            continue
        filtered.append(entry)
    return filtered

def sort_by_date(results):
    results.sort(key=lambda x: x.source.publication_date.to_python_datetime())
    return results