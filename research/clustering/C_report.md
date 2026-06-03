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
3. Nollywood - sparse coverage before 2000s and rich coverage after.


### Results

**Local Gaps**

Hyperparameters.     
C = 3. 
Window is 5%, 10% of the total number of entries. 
For all our queries, this was 20 gaps.

Nollywood has 30 clusters. Election Violence has 100 clusters.  Jay-Jay Okocha has 64 clusters.  
Obviously there aren't 100 chapters in Nigerian election violence, lol.

Raising C = 10.   
Election violence returns 70 clusters. Nollywood 9. Jay-Jay Okocha 6. 

Jay-Jay Okocha:     
6 clusters formed.   
0: 1990-09-10 to 2001-07-27 — 103 entries.  
1: 2002-01-25 to 2003-09-26 — 44 entries.   
2: 2003-11-05 to 2003-12-09 — 3 entries.
3: 2004-01-11 to 2007-11-21 — 153 entries.
4: 2008-02-22 to 2009-09-16 — 64 entries.
5: 2010-01-08 to 2010-12-20 — 33 entries.

Nollywood:
9 clusters formed.
0: 1991-12-30 to 1991-12-30 — 1 entries.
1: 1993-03-29 to 1993-03-29 — 1 entries.
2: 1994-05-02 to 1994-05-02 — 1 entries.
3: 1995-12-05 to 2001-07-12 — 32 entries.
4: 2002-03-15 to 2003-09-12 — 24 entries.
5: 2003-11-28 to 2004-07-02 — 31 entries.
6: 2004-10-22 to 2006-12-20 — 76 entries.
7: 2007-03-09 to 2009-09-30 — 164 entries.
8: 2010-01-06 to 2010-12-24 — 70 entries.

**Jenks Gaps**

When we run Jenks with logs of the gaps, the values appear too similar. 
And we get the algorithm claiming an 11-day gap within a within a 20 year period is important.
Election violence has 212 clusters, lol.

Running Jenks on the raw gaps has much better results.

Election Violence:   
Threshold is 116.5 days and gvf is 0.6527935534560911   

14 clusters formed.
0: 1990-05-14 to 1994-11-08 — 249 entries.
1: 1995-11-02 to 1996-06-13 — 7 entries.
2: 1997-03-07 to 1997-07-03 — 4 entries.
3: 1997-12-04 to 1998-06-29 — 5 entries.
4: 1998-12-02 to 1999-09-06 — 6 entries.
5: 2000-03-06 to 2000-03-06 — 1 entries.
6: 2000-10-09 to 2001-02-05 — 4 entries.
7: 2002-06-25 to 2003-07-17 — 40 entries.
8: 2003-11-27 to 2004-03-04 — 4 entries.
9: 2004-09-29 to 2005-04-28 — 4 entries.
10: 2005-11-07 to 2006-01-26 — 3 entries.
11: 2006-06-15 to 2009-05-11 — 62 entries.
12: 2010-01-18 to 2010-08-16 — 9 entries.
13: 2010-12-15 to 2010-12-20 — 2 entries.

Nollywood:

2026-06-03 16:09:41,549 | INFO | Chronicle_Logger | JENKS BREAK: Threshold is 207.0 days and gvf is 0.7713577668812825
2026-06-03 16:09:41,549 | INFO | Chronicle_Logger | 8 clusters formed.
2026-06-03 16:09:41,549 | INFO | Chronicle_Logger | 0: 1991-12-30 to 1991-12-30 — 1 entries.
1: 1993-03-29 to 1993-03-29 — 1 entries.
2: 1994-05-02 to 1994-05-02 — 1 entries.
3: 1995-12-05 to 1996-08-27 — 5 entries.
4: 1997-06-27 to 1997-12-12 — 2 entries.
5: 1998-08-21 to 1998-09-24 — 2 entries.
6: 1999-06-28 to 2001-07-12 — 23 entries.
7: 2002-03-15 to 2010-12-24 — 365 entries.


Jay-Jay Okocha:


2026-06-03 16:14:18,462 | INFO | Chronicle_Logger | JENKS BREAK: Threshold is 125.5 days and gvf is 0.6838843256119755
2026-06-03 16:14:18,462 | INFO | Chronicle_Logger | 9 clusters formed.
2026-06-03 16:14:18,462 | INFO | Chronicle_Logger | 0: 1990-09-10 to 1990-11-25 — 2 entries.
1: 1991-07-01 to 1991-12-16 — 3 entries.
2: 1992-09-28 to 1992-10-01 — 2 entries.
3: 1993-02-15 to 1993-02-22 — 2 entries.
4: 1993-12-06 to 1993-12-06 — 1 entries.
5: 1994-06-13 to 1994-12-19 — 7 entries.
6: 1995-10-19 to 1996-10-28 — 9 entries.
7: 1997-05-08 to 2001-07-27 — 77 entries.
8: 2002-01-25 to 2010-12-20 — 297 entries.


### Conclusion

The "Jenk Gaps" method is the best and most natural. 

We implement a fail-safe to ensure we are not returning more than 15 clusters.   
In this scenario, we simply cluster along the 14 widest gaps.

We also need to consider dropping sparse clusters.

