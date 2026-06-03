# CLUSTERING

The first phase of Chronicle is running a classic query-driven 
search on the Archivi.NG database, and collecting the results
which are Nigerian news pages.

These pages are then clustered into epochs. Here, we consider
several ways of performing this clustering.


### Clustering Algorithms

**1. Striding**

This is the present, dummy implementation. 
We use a fix a number of clusters N (5, 8, 10 have been tried)
and divide the time period equally between them.


**2. Local Gaps**

Natural gaps in publication dates are probably 
the most honest cluster boundaries. We could:

1. Sort all entries by date (already done)
2. Compute the gap between each consecutive entry
3. Split wherever there's a gap larger than X relative to the local density 
(gap > C × that local median).

The clusters fall out naturally.

**3. Jenked Gaps**

Like technique 2, this starts by finding the natural
gaps in publication dates. We then run K-Means clustering
on these gaps (k=2).

This works under the assumption that they'd be split
into "within-cluster" and "between-cluster" gaps.

We then use the "between-cluster" gaps to determine the clusters.

**4. Time Dynamism**

This is the original suggestion we laid out in the first engineering
document. 

We make N (number of epochs) dynamic based on time span.
For example:     
* < 2 years  → 3 buckets
* 2–5 years  → 5 buckets
* 5–15 years → 8 buckets
* 15+ years  → 10 buckets

Rejected for unsuitability: 
One month of articles tracking a coup escalating piece
by piece might need several clusters; one month of sparse,
unrelated mentions needs one.


### What Makes For Good Clustering

1. Articles within a cluster are about roughly the same chapter of the story.
2. The number of clusters are reasonable for the search.

Queries to test:  
1. Election violence - topic I expect to be cyclical.
2. Jay-Jay Okocha - topic whose "phases" I am familiar with.


### Notes and Stuff

Testing Local Gaps with C = 3, and Window that's 5%, 10% of the entry count.   
Nollywood = 30 clusters. Election Violence = 100 clusters.   
Obviously there aren't 100 chapters in Nigerian election violence, lol.

Raising C to 10, election violence becomes 70, nollywood 9
magic = 2 clusters (4, 35 entries) - 2 month gap.
