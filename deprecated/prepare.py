# prepare.py

from utils.helpers import convertToDate
from utils.log     import setup_logging

logger = setup_logging()

PUBLICATIONS = ["Abuja Newsweek", "AFRICA", "Africa Events", "Africa International", "Africa Now", "Africa Today", "Africa Week", "African Business",
                "African Concord", "African Farmer", "African Review", "AfricanAGE", "AfricAsia", "AfriScope", "Analysis", "Analyst", "Business",
                "Citizen", "Crystal", "DRUM", "Flamingo", "Free Nation", "Insider", "Katsina Newsweek", "National Newsenquiry", "Newbreed", "Newswatch",
                "Nigeria Magazine", "Nigerian Newsweek", "Prime People", "PM News", "Quality", "Sardauna", "Spear", "TELL", "The African Guardian", 
                "The New Nation", "The Nigerian Economist", "The Republic", "The Source", "The Sunday Magazine (TSM)", "TheNEWS", "TheWeek", "Today's People",
                "West Africa"]

def preprocess(results, start_date, end_date, publication):
    return sort_by_date(
        filter_by_publication(
            filter_by_date(results, start_date, end_date), publication))

def hard_filter(results, threshold=0.6):
    '''Shave off any results with semantic relevance scores below a given threshold.'''
    if not results:
        return []
    return [res for res in results if res.semantic_relevance >= threshold]


def filter_by_publication(results, publisher):
    if not publisher or publisher == "All Publishers":
        return results
    if publisher not in PUBLICATIONS:
        error_message = f"{publisher} is not recognized within our publications list: {PUBLICATIONS}"
        logger.error(error_message)
        raise Exception(error_message)
    
    results_by_publisher = []
    for entry in results:
        if entry.source.publication == publisher: 
            results_by_publisher.append(entry)
    return results_by_publisher



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