# CLUSTERING

The first phase of Chronicle is running a classic query-driven 
search on the Archivi.NG database, and collecting the results
which are Nigerian news pages.

These pages are then clustered into epochs. Here, we consider
several ways of performing this clustering.


### Clustering Algorithms

**1. Striding**

This is the present implementation. 
We use a fix a number of clusters N (5, 8, 10 have been tried)
and divide the time period equally between them.

**2. Time Dynamism**

We can make the number of clusters N dynamic based on time span.
* < 2 years  → 3 buckets
* 2–5 years  → 5 buckets
* 5–15 years → 8 buckets
* 15+ years  → 10 buckets

**3. Gap Detection**

Natural gaps in publication dates are probably 
the most honest cluster boundaries. We could:

1. Sort all entries by date (already done)
2. Compute the gap between each consecutive entry
3. Find all gaps greater than 3 months. 
4. Clusters fall out naturally

This is called "jenks natural breaks" in data visualization.
