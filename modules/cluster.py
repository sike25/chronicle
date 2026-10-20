from utils.log import setup_logging

logger = setup_logging()

MAX_CLUSTERS = 10

def cluster_into_buckets(entries):
    return cluster_by_clustering_gaps(entries)

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

    if len(entries) == 1:
        logger.info("cluster_by_clustering_gaps: single entry — returning single cluster.")
        return _single_cluster(entries)

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

    if n < 2:
        logger.info("_jenks_break_K2: only one gap value — returning it as threshold.")
        return values[0], 0.0

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
