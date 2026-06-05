import statistics
import math

from datetime  import timedelta
from utils.log import setup_logging

logger = setup_logging()

MAX_CLUSTERS = 15

def cluster_into_buckets(entries):
    return cluster_by_clustering_gaps(entries)

def cluster_by_local_gaps(entries):
    '''
    EXPERIMENTAL. 
    Groups entries into chronological epochs based on
    locally distinct time gaps in publication dates.


    A gap is a boundary if it exceeds C times the median of the gaps
    immediately surrounding it (a window of `window` gaps on each side).
    Because the window is defined by entry *count*, it auto-scales with
    density: in a dense burst the local rhythm is days, in a sparse
    stretch it's months, and the same C means the same thing in both.
    '''
    
    if not entries:
        logger.warning("Cluster function received an empty entries list.")
        return {}
    
    N = len(entries)
    C = 10
    W = int(int(0.1 * N) / 2) # length of window on one side.

    logger.info(f"WINDOW LENGTH: {W}")

    if W < 1: return _single_cluster(entries)

    gaps = _day_gaps(entries)
    boundaries = []
    for idx, gap in enumerate(gaps):

        window_start = max(0,           idx-W)
        window_end   = min(len(gaps)-1, idx+W)
        gaps_in_window = gaps[window_start:idx] + gaps[idx+1:window_end+1]

        local_median = statistics.median(gaps_in_window)
        if gap > C * local_median:
            boundaries.append(idx)

    if not boundaries:
        logger.info("cluster_by_local_gaps: no anomalous gaps found. Single cluster.")
        return _single_cluster(entries)
    
    return _split_at_boundaries(entries, boundaries)
    


def cluster_by_clustering_gaps(entries):
    '''
    Groups entries into chronological epochs based on
    important gaps selected via K-Means.

    Treats the set of inter-article gaps as a 1D dataset, and clusters
     it into two populations — within-story (small) and between-story (large) 
     — via Jenks natural breaks. Every gap in the large population is a boundary.
    '''
    if not entries:
        logger.warning("cluster_by_clustering_gaps: received an empty entries list.")
        return {}

    gaps = _day_gaps(entries)
    threshold, _ = _jenks_break_K2(gaps)
    
    boundaries = [idx for idx, gap in enumerate(gaps) if (gap > threshold)]
    if not boundaries:
        logger.info("cluster_by_jenk_gaps: no anomalous gaps found. Single cluster.")
        return _single_cluster(entries)

    # Fail safe: Never return more than MAX_CLUSTERS
    # When Jenks produces too many, keep only the widest gaps.
    if len(boundaries) > MAX_CLUSTERS - 1:
        logger.info(
            f"cluster_by_clustering_gaps: {len(boundaries) + 1} clusters exceeds "
            f"cap of {MAX_CLUSTERS}. Falling back to the {MAX_CLUSTERS - 1} widest gaps."
        )
        widest = sorted(range(len(gaps)), key=lambda i: gaps[i], reverse=True)[:MAX_CLUSTERS - 1]
        boundaries = sorted(widest)
    
    return _split_at_boundaries(entries, boundaries)


def cluster_by_stride(entries, nb_buckets):
    '''
    DEPRECATED. original dummy implementation.

    Groups entries into chronological clusters 
    based on a fixed time stride.
    '''
    
    if not entries:
        logger.warning("Cluster request received an empty entries list.")
        return {}

    first_entry = entries[0].source
    last_entry  = entries[-1].source

    first_date = first_entry.publication_date.to_python_datetime()
    last_date  = last_entry.publication_date.to_python_datetime()

    duration = last_date - first_date

    logger.info(f"First result: {first_entry.filename} on {first_date}")
    logger.info(f"Last  result: {last_entry.filename}  on {last_date} ")
    logger.debug(f"The search results span {duration.days} days.")

    # handle short durations
    if duration < timedelta(days=30):
        logger.info("Short duration detected (<30 days). Returning single cluster.")
        label = f"{first_date} to {last_date}"
        return {label: entries}

    stride = duration / nb_buckets
    
    buckets = {}
    for i in range(nb_buckets):
        b_start = first_date + (stride * i)
        b_end   = first_date + (stride * (i + 1))
        
        label = f"{b_start} to {b_end}"
        buckets[label] = []
        
        for entry in entries:
            entry_date = entry.source.publication_date.to_python_datetime()
            
            # the very last bucket is inclusive of the last_date
            if i == nb_buckets - 1:
                if b_start <= entry_date <= last_date:
                    buckets[label].append(entry)
            else:
                if b_start <= entry_date < b_end:
                    buckets[label].append(entry)
        
    # drop empty clusters
    return {k: v for k, v in buckets.items() if v}


### HELPERS --------------------------------------------------------------------------------

def _jenks_break_K2(values):
    '''
    Otsu splits values array into two classes,
    by minimizing the in-class standard deviation.
    Returns (threshold, goodness_of_variance_fit), or (None, 0.0) if the
    values are all identical (no split possible).

    O(n^2), trivial at n <= 399 gaps.
    '''
    values = sorted(values)
    n      = len(values)
    mean   = sum(values) / n

    logger.info(f"GAPS: {values}")

    # standard deviations from array mean
    sdam = sum((v - mean) ** 2 for v in values)
    
    best_sdcm = None
    best_idx  = None
    for i in range(n - 1):
        lower_values, upper_values = values[:i + 1], values[i + 1:] 

        lower_mean = sum(lower_values) / len(lower_values)
        upper_mean = sum(upper_values) / len(upper_values)

        lower_sdcm = sum((x - lower_mean) ** 2 for x in lower_values)
        upper_sdcm = sum((x - upper_mean) ** 2 for x in upper_values)
        sdcm       = lower_sdcm + upper_sdcm

        if best_sdcm is None or sdcm < best_sdcm:
            best_sdcm, best_idx = sdcm, i

    gvf = (sdam - best_sdcm) / sdam
    threshold = (values[best_idx] + values[best_idx + 1]) / 2

    logger.info(f"JENKS BREAK: Threshold is {threshold} days and gvf is {gvf}")
    return threshold, gvf


    

def _split_at_boundaries(entries, boundaries):
    '''
    Splits entries into epochs, according to boundary indices provided. 
    A boundary index i means there's a break
    between entry[i] and entry[i+1]. 
    
    Returns {date_range_label: [entries]}.
    '''

    epochs, start = [], 0
    for boundary in boundaries:
        epochs.append(entries[start:boundary+1])
        start = boundary + 1
    epochs.append(entries[start:])

    buckets = {}
    for epoch in epochs:
        label = f"{_date_of(epoch[0])} to {_date_of(epoch[-1])}"
        # disambiguate the rare case of >1 single-day segments sharing a label.
        if label in buckets:
            label = f"{label} ({len(buckets)})"
        buckets[label] = epoch

    return buckets

def _day_gaps(entries):
    '''
    Consecutive gaps in days. 
    '''
    dates = [_date_of(entry) for entry in entries]
    return [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

def _single_cluster(entries):
    d0, d1 = _date_of(entries[0]), _date_of(entries[-1])
    return {f"{d0} to {d1}": entries}

def _date_of(entry):
    return entry.source.publication_date.to_python_datetime()
