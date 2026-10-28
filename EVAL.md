# Evaluation report

This is the report on what you built and what the numbers let you claim.
Two kinds of text live here.

The tables between a `p2:begin` comment line and its matching `p2:end` comment line are written by `uv run p2 score` from your committed run files and answers files.
Please do not edit anything between those two lines, because `uv run p2 check` recomputes them and fails when they differ.
A table that says no runs or answers exist yet is waiting for data; run `uv run p2 score` after you commit the files it needs.

Everything else is yours.
Each prompt ends with a marker line that you replace with your own writing; `uv run p2 check --final` fails while one is left.
Write what you measured, including what did not work.
What I read for is whether each claim matches its interval, not whether the result is good news.

Words used below: recall@10, MRR@10 and nDCG@10 are the three scores, each averaged over the queries of a set; step 7 of stage 1 in the README defines them, and lecture 14 goes deeper.
A paired interval is the 95% interval of the mean difference between two systems on the same queries, found by resampling the queries 10,000 times.
When an interval includes zero, the gold set cannot tell the two systems apart, and the right words are "not distinguishable on this gold set".
The minimum detectable difference is the smallest gap this many queries could reliably show, so a difference below it is invisible to this gold set, not absent.

---

## 1. Stage 1 - the shared corpus (30 CFR Chapter I)

### What you built

For each of `dense`, `hybrid` and `rerank`, one or two sentences: the embedding model, how documents were chunked, what was fused and how, how many candidates the reranker saw, and anything you changed from the 12 and 13 lab code.

`dense`: embeds each 300-word chunk (50-word overlap) with `BAAI/bge-small-en-v1.5` and ranks chunks by cosine similarity to the query, which is embedded without a prefix. A document's score is its best chunk's.

`hybrid`: combines `bm25` and `dense` with reciprocal rank fusion, scoring each document by the sum of 1 / (60 + rank) over both rankings. Each system ranks every document. 

`rerank`: takes the top 20 documents of `hybrid`, each cut to its first 600 characters, and asks Claude in one call to put all 20 in order, best first. An invalid or failed reply keeps hybrid's order, and documents below the top 20 keep their place. 

Changed from the lab code: the labs ranked whole articles, while mine cut 300-word chunks, score a document by its best chunk, and add a `search_chunks` path for answers. The lab's constants (20 candidates, 600 characters) and the model, RRF constant and first stage are set in `p2.toml`. My rerank prompt says "a document collection" instead of "a help center", and its reply schema also bounds each number between 1 and n.

### Practice queries (20)

Scores per system.

<!-- p2:begin shared-practice -->
| System | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| bm25 | 0.625 | 0.507 | 0.518 |
| dense | 0.558 | 0.562 | 0.480 |
| hybrid | 0.592 | 0.471 | 0.443 |
| rerank | 0.758 | 0.800 | 0.756 |

20 judged queries; nDCG uses binary labels; a random ranking of the 2,484 documents would get recall@10 near 0.004.
<!-- p2:end shared-practice -->

The same scores per query class.

<!-- p2:begin shared-practice-classes -->
| System | Metric | identifier (n=7) | paraphrase (n=7) | mixed (n=6) |
| --- | --- | ---: | ---: | ---: |
| bm25 | Recall@10 | 1.000 | 0.000 | 0.917 |
| bm25 | MRR@10 | 0.810 | 0.000 | 0.746 |
| bm25 | nDCG@10 | 0.857 | 0.000 | 0.728 |
| dense | Recall@10 | 0.214 | 0.595 | 0.917 |
| dense | MRR@10 | 0.333 | 0.714 | 0.653 |
| dense | nDCG@10 | 0.211 | 0.593 | 0.661 |
| hybrid | Recall@10 | 0.500 | 0.405 | 0.917 |
| hybrid | MRR@10 | 0.514 | 0.152 | 0.792 |
| hybrid | nDCG@10 | 0.397 | 0.202 | 0.779 |
| rerank | Recall@10 | 0.714 | 0.595 | 1.000 |
| rerank | MRR@10 | 0.714 | 0.714 | 1.000 |
| rerank | nDCG@10 | 0.690 | 0.626 | 0.987 |
<!-- p2:end shared-practice-classes -->

Differences between every pair of systems, each with its paired interval and the minimum detectable difference.

<!-- p2:begin shared-practice-pairs -->
| Comparison | Metric | Mean difference | 95% interval | MDD | Reading |
| --- | --- | ---: | ---: | ---: | --- |
| dense minus bm25 | Recall@10 | -0.067 | [-0.350, +0.225] | 0.415 | not distinguishable |
| dense minus bm25 | MRR@10 | +0.055 | [-0.225, +0.343] | 0.412 | not distinguishable |
| dense minus bm25 | nDCG@10 | -0.039 | [-0.302, +0.231] | 0.385 | not distinguishable |
| hybrid minus bm25 | Recall@10 | -0.033 | [-0.250, +0.192] | 0.324 | not distinguishable |
| hybrid minus bm25 | MRR@10 | -0.037 | [-0.178, +0.083] | 0.192 | not distinguishable |
| hybrid minus bm25 | nDCG@10 | -0.075 | [-0.238, +0.075] | 0.228 | not distinguishable |
| hybrid minus dense | Recall@10 | +0.033 | [-0.125, +0.192] | 0.231 | not distinguishable |
| hybrid minus dense | MRR@10 | -0.092 | [-0.306, +0.109] | 0.301 | not distinguishable |
| hybrid minus dense | nDCG@10 | -0.036 | [-0.200, +0.113] | 0.227 | not distinguishable |
| rerank minus bm25 | Recall@10 | +0.133 | [-0.100, +0.358] | 0.340 | not distinguishable |
| rerank minus bm25 | MRR@10 | +0.293 | [+0.043, +0.533] | 0.353 | rerank higher |
| rerank minus bm25 | nDCG@10 | +0.238 | [+0.008, +0.458] | 0.328 | rerank higher |
| rerank minus dense | Recall@10 | +0.200 | [+0.050, +0.367] | 0.224 | rerank higher |
| rerank minus dense | MRR@10 | +0.237 | [+0.083, +0.408] | 0.239 | rerank higher |
| rerank minus dense | nDCG@10 | +0.277 | [+0.136, +0.432] | 0.216 | rerank higher |
| rerank minus hybrid | Recall@10 | +0.167 | [+0.058, +0.292] | 0.166 | rerank higher |
| rerank minus hybrid | MRR@10 | +0.329 | [+0.164, +0.504] | 0.247 | rerank higher |
| rerank minus hybrid | nDCG@10 | +0.313 | [+0.186, +0.444] | 0.188 | rerank higher |

The interval is a paired bootstrap (10,000 resamples of the queries); MDD is the smallest difference this many queries detect 80% of the time.
<!-- p2:end shared-practice-pairs -->

The 40 test queries have no answer key in this repo.
Your test run files are scored by the course and the score comes back to you as feedback, so nothing goes here for them.

### What the intervals let you claim

Which differences are distinguishable from zero and which are not?
What is the minimum detectable difference at 20 queries, and what does that say about any gap smaller than it?
Which claim from lecture 12 or 13 did your numbers support, and which did they leave open?


On the 20 practice queries, rerank is distinguishably better than hybrid and dense on all three metrics, and better than bm25 on MRR@10 and nDCG@10 (but not Recall@10, and with lower ends barely above zero). None of the differences among bm25, dense and hybrid is distinguishable. The minimum detectable differences are 0.17 to 0.42, so a gap smaller than that could be hidden, and “not distinguishable” here does not mean equal.

The class table fits lecture 12’s claim that no retriever wins everywhere: bm25 is best on identifier queries and scores 0 on paraphrase queries, dense is best on paraphrase queries, and even rerank trails bm25 on identifiers. With 6 or 7 queries per class and no intervals, I treat this as a pattern, not a tested result. `hybrid` did not beat its better component on the identifier or paraphrase queries, but on the 6 mixed queries it did (MRR@10 0.792 against `bm25` 0.746 and `dense` 0.653).

Lecture 13 said each stage after the first retriever can help on average and can hurt on your data. My numbers support that for rerank, which is distinguishably better than hybrid, and leave it open for fusion, since no hybrid comparison is distinguishable. The class table also fits lecture 13’s point that fusion helps the weaker partner and hurts the stronger one: hybrid sits between bm25 and dense in the identifier and paraphrase classes. The lecture’s warning that a reranker cannot recover documents outside its 20 candidates is consistent with rerank trailing bm25 on identifier queries, but I have not checked which of its misses were outside the candidate list.

---

## 2. Stage 1 - cited answers on the 12 shared questions

<!-- p2:begin answers -->
| Label | System | Verified (in) | 95% interval | not_found (in) | Declined (out) | 95% interval | Quotes found |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| rerank | rerank | 8 of 8 (100%) | [0.676, 1.000] | 0 of 8 (0%) | 4 of 4 (100%) | [0.510, 1.000] | 13 of 13 |
<!-- p2:end answers -->

Which system answered, and why that one?
What did you change in `prompts/answer.txt`, if anything, and did the verified share or the declined share move?

Then read three in-corpus answers that `uv run p2 verify` passed.
For each one, open the cited chunk and say whether the quote really supports the claim next to it.
The check proves a quote is a real piece of the chunk and cannot prove that it supports the claim, so this reading is the part only you can do.


The system that answered is `rerank` as it had the best practice-query scores: Recall@10 0.758, MRR@10 0.800, nDCG@10 0.756; answering with it cost two Claude calls per question.

`prompts/answer.txt` is unchanged since the initial commit. 

The verified share (8 of 8) and the declined share (4 of 4) both come from the starting prompt, and all three repeats gave the same counts.

Audit a08: supported yes (for the cited claim) - paragraph (b)(1) of `cfr30-7.506#0` says the breathable air "sustains each person for 96 hours," which is the number the claim states. The answer text also adds a sentence about a 48-hour alternative that has no claim or quote behind it, and `cfr30-7.506#0` does not contain it. It appears in `cfr30-75.1507` (paragraphs (c) and (d)(1)), which was among the five retrieved chunks, so it looks grounded, but the check passed without testing it because it only reads claims.

Audit a02: supported yes for claim 1, partly for claim 2 - the 80 percent quote matches the first sentence of `cfr30-75.403#0` word for word. Claim 2 says the percentage is increased "only" where methane is present, but the chunk only says it is increased by 0.4 percent per 0.1 percent of methane where methane is present. The word "only" is an inference from the two sentences together, not something the quote states.

Audit a07: supported yes for the height requirement, no for the scope sentence - paragraph (b) of both `cfr30-57.9300#0` and `cfr30-56.9300#0` contains the mid-axle sentence, so both quotes are real and support their claims. The answer also says 57.9300 covers underground and surface mines while 56.9300 covers surface mines only, and neither chunk says which mines each section applies to, so that part is not supported by the cited text. 

---

## 3. Stage 2 - your corpus and your gold set

### The corpus

What is it, where did it come from, how many documents and how many megabytes, and what is the license basis for publishing it?
Name the one or two documents you were least sure about and what you decided.
Say which of the allowed sources in the brief it comes from.

The corpus: "The USGS Mineral Commodity Summaries" per-commodity chapter PDFs, from pubs.usgs.gov/periodicals/mcsYYYY/. All 262 manifest rows point there, and `scripts/fetch_usgs.sh` is the fetch script. There are 262 documents: 87 from the 2024 edition, 87 from 2025, and 88 from 2026. This is 2.0 MB of markdown. All 262 rows say `us-gov-public-domain`. `LICENSES.md` shows 262 ok, 0 flagged, 0 fail, 0 reviewed. All 262 manifest sources are usgs.gov addresses. 

Each volume's front matter makes one reservation. Page 4 of the 2024 volume, https://pubs.usgs.gov/periodicals/mcs2024/mcs2024.pdf. Page 4 of the 2025 volume, https://pubs.usgs.gov/periodicals/mcs2025/mcs2025.pdf. Page 4 of the 2026 volume, https://pubs.usgs.gov/periodicals/mcs2026/mcs2026.pdf. “Although this report is in the public domain, permission must be secured from the individual copyright owners to reproduce any copyrighted material contained within this report.” None of the 262 documents contains "copyright", “©” or “permission”, so the corpus holds only USGS text, which the volume itself calls public domain.

License basis: “USGS-authored or produced data and information are considered to be in the U.S. public domain and can be freely used without permission.” 
The exception: “Not all information, illustrations, or photographs on our site are” in the public domain. Some non-USGS images are used with the copyright holder’s permission and “are generally marked as being copyrighted”. 

Source: https://www.usgs.gov/faqs/are-usgs-reportspublications-copyrighted

Least-sure documents: I was not doubtful of documents since each of the 262 documents were from usgs.gov addresses.

### The gold set

How many queries, how many with origin `hand` and how many with origin `claude`, and which query classes did you use and why?
How did you decide that a document is relevant: write your relevance rule in two or three sentences, the way the brief does for the shared corpus.
How did you find candidates (the systems' top 10, a keyword search, reading), and did you read every document before you labeled it?
Your labels are binary (`rel` 1) unless you say otherwise: if you use graded labels, declare the scale here, for example 2 means the document answers the query fully and 1 means it helps.

A chapter is relevant to a query if it contains the information that answers the question as asked, meaning the commodity,
country, statistic or trend the query is about is stated in the chapter’s text or tables; a chapter that only mentions the
commodity without answering the question is not relevant. When a query names a year, I treat it as the data year, the year
the figure describes, not the year of the edition that publishes it, and every chapter that reports a figure for that year
is relevant, whether the figure is an estimate or a revised value. When a query names no year, the matching chapter from
any edition counts as relevant. The exception is a query that names the publication itself (for example, “Mineral Commodity
Summaries 2025”): there the year refers to the edition, and only that edition’s chapters count. I fixed this rule before
judging and will not change it after seeing results.

There were 38 queries consisting of 10 by `hand` and 28 from `claude`. There were two classes used: `paraphrase` and `keyword` and it is split evenly: `hand` has 5 paraphrase and 5 keyword, `claude` has 14 and 14, so 19 and 19 overall.

`paraphrase` and `keyword` were used since `bm25` is strong on exact terms while `dense` works well with paraphrasing. 

I grepped keywords like the commodity name, country, and year and then read the chapter that I found to see if it pertained to query. I did also work from `.cache/candidates.md` to find relevance in the pool of documents. For each of the chapters that I labeled, I skimmed the sibling editions. 

The size of the set was 120 judgments, 1–6 relevant per query, and most had 3.
Additionally, the labels are binary.

---

## 4. Stage 2 - results on your corpus

Scores per system on your gold set.

<!-- p2:begin own -->
| System | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| bm25 | 0.851 | 0.767 | 0.786 |
| dense | 0.787 | 0.722 | 0.731 |
| hybrid | 0.871 | 0.823 | 0.825 |
| rerank | 0.939 | 0.947 | 0.930 |
| ablation/dense_small | 0.855 | 0.798 | 0.808 |

38 judged queries; nDCG uses binary labels; a random ranking of the 262 documents would get recall@10 near 0.038.
<!-- p2:end own -->

The same scores per query class.

<!-- p2:begin own-classes -->
| System | Metric | paraphrase (n=19) | keyword (n=19) |
| --- | --- | ---: | ---: |
| bm25 | Recall@10 | 0.702 | 1.000 |
| bm25 | MRR@10 | 0.622 | 0.912 |
| bm25 | nDCG@10 | 0.629 | 0.944 |
| dense | Recall@10 | 0.575 | 1.000 |
| dense | MRR@10 | 0.471 | 0.974 |
| dense | nDCG@10 | 0.481 | 0.981 |
| hybrid | Recall@10 | 0.741 | 1.000 |
| hybrid | MRR@10 | 0.699 | 0.947 |
| hybrid | nDCG@10 | 0.684 | 0.967 |
| rerank | Recall@10 | 0.877 | 1.000 |
| rerank | MRR@10 | 0.921 | 0.974 |
| rerank | nDCG@10 | 0.882 | 0.977 |
| ablation/dense_small | Recall@10 | 0.711 | 1.000 |
| ablation/dense_small | MRR@10 | 0.623 | 0.974 |
| ablation/dense_small | nDCG@10 | 0.639 | 0.977 |
<!-- p2:end own-classes -->

The same scores for the queries you wrote yourself (`hand`) and the ones a model drafted (`claude`), with the difference between the two groups and its interval.
Once both groups have queries, the table also says whether `bm25`'s lead over `dense` differs between them, and what share of each query's content words its best relevant document contains, which is stretch option 6.

<!-- p2:begin own-origins -->
| System | Metric | hand (n=10) | claude (n=28) | hand minus claude | 95% interval | Reading |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| bm25 | Recall@10 | 0.750 | 0.887 | -0.137 | [-0.426, +0.108] | not distinguishable |
| bm25 | MRR@10 | 0.683 | 0.797 | -0.114 | [-0.408, +0.157] | not distinguishable |
| bm25 | nDCG@10 | 0.705 | 0.815 | -0.110 | [-0.395, +0.142] | not distinguishable |
| dense | Recall@10 | 0.825 | 0.774 | +0.051 | [-0.196, +0.267] | not distinguishable |
| dense | MRR@10 | 0.814 | 0.690 | +0.125 | [-0.167, +0.379] | not distinguishable |
| dense | nDCG@10 | 0.788 | 0.710 | +0.077 | [-0.192, +0.317] | not distinguishable |
| hybrid | Recall@10 | 0.892 | 0.863 | +0.029 | [-0.148, +0.195] | not distinguishable |
| hybrid | MRR@10 | 0.860 | 0.810 | +0.050 | [-0.185, +0.254] | not distinguishable |
| hybrid | nDCG@10 | 0.838 | 0.820 | +0.018 | [-0.195, +0.210] | not distinguishable |
| rerank | Recall@10 | 1.000 | 0.917 | +0.083 | [+0.006, +0.179] | hand higher |
| rerank | MRR@10 | 0.950 | 0.946 | +0.004 | [-0.114, +0.125] | not distinguishable |
| rerank | nDCG@10 | 0.976 | 0.913 | +0.063 | [-0.023, +0.161] | not distinguishable |
| ablation/dense_small | Recall@10 | 0.867 | 0.851 | +0.015 | [-0.229, +0.225] | not distinguishable |
| ablation/dense_small | MRR@10 | 0.783 | 0.804 | -0.020 | [-0.287, +0.223] | not distinguishable |
| ablation/dense_small | nDCG@10 | 0.797 | 0.812 | -0.015 | [-0.261, +0.204] | not distinguishable |

The hand and claude queries are different queries, so the interval of hand minus claude comes from resampling the queries within each group (10,000 times), not from pairing them.

Do model-written queries favor keyword search? bm25's lead over dense (bm25 minus dense, per query) on the claude queries and on the hand queries, and claude minus hand:

| Metric | Lead on claude | Lead on hand | Claude minus hand | 95% interval | Reading |
| --- | ---: | ---: | ---: | ---: | --- |
| Recall@10 | +0.113 | -0.075 | +0.188 | [-0.129, +0.488] | not distinguishable |
| MRR@10 | +0.108 | -0.131 | +0.239 | [-0.106, +0.572] | not distinguishable |
| nDCG@10 | +0.105 | -0.082 | +0.187 | [-0.106, +0.452] | not distinguishable |

Mean content-word overlap, the share of a query's content words found in its best relevant document: hand 0.69 (10 queries), claude 0.81 (28 queries).

Stretch option 6 asks for at least 20 judged queries of each origin; here there are 10 hand and 28 claude.
<!-- p2:end own-origins -->

Differences between every pair of systems.

<!-- p2:begin own-pairs -->
| Comparison | Metric | Mean difference | 95% interval | MDD | Reading |
| --- | --- | ---: | ---: | ---: | --- |
| dense minus bm25 | Recall@10 | -0.064 | [-0.184, +0.057] | 0.174 | not distinguishable |
| dense minus bm25 | MRR@10 | -0.045 | [-0.177, +0.081] | 0.183 | not distinguishable |
| dense minus bm25 | nDCG@10 | -0.056 | [-0.173, +0.051] | 0.160 | not distinguishable |
| hybrid minus bm25 | Recall@10 | +0.020 | [-0.066, +0.101] | 0.121 | not distinguishable |
| hybrid minus bm25 | MRR@10 | +0.056 | [-0.039, +0.153] | 0.139 | not distinguishable |
| hybrid minus bm25 | nDCG@10 | +0.039 | [-0.039, +0.119] | 0.114 | not distinguishable |
| hybrid minus dense | Recall@10 | +0.083 | [+0.018, +0.167] | 0.108 | hybrid higher |
| hybrid minus dense | MRR@10 | +0.101 | [+0.023, +0.193] | 0.122 | hybrid higher |
| hybrid minus dense | nDCG@10 | +0.094 | [+0.026, +0.176] | 0.108 | hybrid higher |
| rerank minus bm25 | Recall@10 | +0.088 | [+0.018, +0.180] | 0.119 | rerank higher |
| rerank minus bm25 | MRR@10 | +0.180 | [+0.077, +0.292] | 0.154 | rerank higher |
| rerank minus bm25 | nDCG@10 | +0.143 | [+0.062, +0.236] | 0.124 | rerank higher |
| rerank minus dense | Recall@10 | +0.151 | [+0.070, +0.248] | 0.129 | rerank higher |
| rerank minus dense | MRR@10 | +0.225 | [+0.104, +0.359] | 0.184 | rerank higher |
| rerank minus dense | nDCG@10 | +0.199 | [+0.101, +0.310] | 0.152 | rerank higher |
| rerank minus hybrid | Recall@10 | +0.068 | [+0.015, +0.138] | 0.091 | rerank higher |
| rerank minus hybrid | MRR@10 | +0.124 | [+0.030, +0.232] | 0.145 | rerank higher |
| rerank minus hybrid | nDCG@10 | +0.105 | [+0.036, +0.187] | 0.109 | rerank higher |
| ablation/dense_small minus bm25 | Recall@10 | +0.004 | [-0.110, +0.123] | 0.167 | not distinguishable |
| ablation/dense_small minus bm25 | MRR@10 | +0.031 | [-0.085, +0.145] | 0.165 | not distinguishable |
| ablation/dense_small minus bm25 | nDCG@10 | +0.022 | [-0.074, +0.116] | 0.135 | not distinguishable |
| ablation/dense_small minus dense | Recall@10 | +0.068 | [-0.022, +0.169] | 0.138 | not distinguishable |
| ablation/dense_small minus dense | MRR@10 | +0.076 | [-0.029, +0.185] | 0.155 | not distinguishable |
| ablation/dense_small minus dense | nDCG@10 | +0.078 | [-0.012, +0.176] | 0.135 | not distinguishable |
| ablation/dense_small minus hybrid | Recall@10 | -0.015 | [-0.092, +0.070] | 0.119 | not distinguishable |
| ablation/dense_small minus hybrid | MRR@10 | -0.025 | [-0.121, +0.072] | 0.142 | not distinguishable |
| ablation/dense_small minus hybrid | nDCG@10 | -0.017 | [-0.093, +0.064] | 0.115 | not distinguishable |
| ablation/dense_small minus rerank | Recall@10 | -0.083 | [-0.189, +0.018] | 0.148 | not distinguishable |
| ablation/dense_small minus rerank | MRR@10 | -0.149 | [-0.281, -0.026] | 0.185 | rerank higher |
| ablation/dense_small minus rerank | nDCG@10 | -0.122 | [-0.229, -0.018] | 0.152 | rerank higher |

The interval is a paired bootstrap (10,000 resamples of the queries); MDD is the smallest difference this many queries detect 80% of the time.
<!-- p2:end own-pairs -->

Which differences are distinguishable and which are not, at your gold-set size?
Do the `hand` queries and the `claude` queries tell the same story?
Did your prediction in `DECISIONS.md` prompt 1 hold?

TODO: write what your own-corpus intervals let you claim.

---

## 5. The ablation

Change one thing and keep everything else the same.
Write your hypothesis here before you run it, in one sentence with a direction: I expect reducing the dense retriever’s chunk size from 300 to 100 words to
raise dense MRR@10 on my corpus, because the sentence that answers a paraphrase query is a small part of a 300-word chunk, so its embedding is diluted by the
surrounding boilerplate that every commodity chapter shares.
The run file for it lives in `runs/own/ablation/`.

<!-- p2:begin own-ablation -->
| Comparison | Metric | Mean difference | 95% interval | MDD | Reading |
| --- | --- | ---: | ---: | ---: | --- |
| ablation/dense_small minus bm25 | Recall@10 | +0.004 | [-0.110, +0.123] | 0.167 | not distinguishable |
| ablation/dense_small minus bm25 | MRR@10 | +0.031 | [-0.085, +0.145] | 0.165 | not distinguishable |
| ablation/dense_small minus bm25 | nDCG@10 | +0.022 | [-0.074, +0.116] | 0.135 | not distinguishable |
| ablation/dense_small minus dense | Recall@10 | +0.068 | [-0.022, +0.169] | 0.138 | not distinguishable |
| ablation/dense_small minus dense | MRR@10 | +0.076 | [-0.029, +0.185] | 0.155 | not distinguishable |
| ablation/dense_small minus dense | nDCG@10 | +0.078 | [-0.012, +0.176] | 0.135 | not distinguishable |
| ablation/dense_small minus hybrid | Recall@10 | -0.015 | [-0.092, +0.070] | 0.119 | not distinguishable |
| ablation/dense_small minus hybrid | MRR@10 | -0.025 | [-0.121, +0.072] | 0.142 | not distinguishable |
| ablation/dense_small minus hybrid | nDCG@10 | -0.017 | [-0.093, +0.064] | 0.115 | not distinguishable |
| ablation/dense_small minus rerank | Recall@10 | -0.083 | [-0.189, +0.018] | 0.148 | not distinguishable |
| ablation/dense_small minus rerank | MRR@10 | -0.149 | [-0.281, -0.026] | 0.185 | rerank higher |
| ablation/dense_small minus rerank | nDCG@10 | -0.122 | [-0.229, -0.018] | 0.152 | rerank higher |

The interval is a paired bootstrap (10,000 resamples of the queries); MDD is the smallest difference this many queries detect 80% of the time.
<!-- p2:end own-ablation -->

The queries your ablation helped and hurt, against the system it varies, by reciprocal rank.
`p2 score` finds that system from a line such as `BASE = "bm25"` in your variant's file, or else from its name: `bm25_lab` varies `bm25`.

<!-- p2:begin own-ablation-queries -->
ablation/dense_small against dense (BASE = "dense" in p2/retrievers/dense_small.py): it helped 8 queries, hurt 4 and left 26 unchanged.

| Query | Class | Origin | dense RR | ablation/dense_small RR | Change | Effect |
| --- | --- | --- | ---: | ---: | ---: | --- |
| o18 | paraphrase | claude | 0.000 | 1.000 | +1.000 | helped |
| o21 | paraphrase | claude | 0.143 | 1.000 | +0.857 | helped |
| o13 | paraphrase | claude | 0.167 | 1.000 | +0.833 | helped |
| o11 | paraphrase | claude | 0.500 | 1.000 | +0.500 | helped |
| o33 | keyword | claude | 0.500 | 1.000 | +0.500 | helped |
| o04 | paraphrase | hand | 0.143 | 0.500 | +0.357 | helped |
| o03 | paraphrase | hand | 0.000 | 0.333 | +0.333 | helped |
| o23 | paraphrase | claude | 0.250 | 0.500 | +0.250 | helped |
| o05 | paraphrase | hand | 1.000 | 0.000 | -1.000 | hurt |
| o35 | keyword | claude | 1.000 | 0.500 | -0.500 | hurt |
| o17 | paraphrase | claude | 0.125 | 0.000 | -0.125 | hurt |
| o22 | paraphrase | claude | 0.125 | 0.000 | -0.125 | hurt |

RR is the reciprocal rank of the first relevant document in the top 10 (0 when none is there), the per-query value behind MRR@10; the queries at the top of each list are the ones to read.
<!-- p2:end own-ablation-queries -->

What did you change, what happened, and does the interval support the claim you want to make?
If the result is not distinguishable, say what size of effect your gold set could have seen.
Read the queries at the top of each list in the second table, and say whether your change explains them.

Change: I reduced the dense retriever’s chunk size from 300 to 100 words in a variant, dense_small, and left the overlap at 50 words. Nothing else changed, and
the variant is compared with dense.

Hypothesis (written before the run): this would raise dense MRR@10 on my corpus, because the sentence that answers a paraphrase query is a small part of a
300-word chunk, so its embedding is diluted by the boilerplate every commodity chapter shares.

Result: MRR@10 rose by +0.076, 95% interval [−0.029, +0.185]. The direction matches the hypothesis, but the interval includes zero, so the result is not
distinguishable. nDCG@10 (+0.078, [−0.012, +0.176]) and Recall@10 (+0.068, [−0.022, +0.169]) tell the same story. The MDD for this comparison was 0.155, so my
38 queries could detect a gain of about that size and could not detect one of +0.076. A true effect anywhere from a small harm to roughly +0.19 is still
possible.

Claim: the data do not show that smaller chunks help dense, and they do not show that they hurt. Reading the intervals the same four-row way as my PREREG §4
test (which was written in advance only for hybrid vs bm25), the hypothesis is not supported.

Query lists: dense_small helped 8 queries, hurt 4 and left 26 unchanged, and 7 of the 8 helped are paraphrase queries. In the three biggest wins (o18, o21,
o13), dense ranked the right chapter outside its top three, while dense_small ranked a chunk that echoes the query first: the garnet Substitutes paragraph
mentioning sandblasting, the opening chunk of all three tin editions (“not mined… since 1993”), and a bismuth chunk with the pharmaceutical sentence. Only the
tin chunk holds the answer sentence itself, and I did not check the others for the stomach-remedy or 1997 clues. So a narrower window helped here, but this does
not show that an answer sentence was diluted. Of the 4 hurt queries, o05 lost its one relevant chunk (the heavy rare earths chunk about permanent magnets) to
vanadium, cobalt and lithium chunks, which alone lowered the mean difference by about 0.026 (1/38). In o35, dense_small ranked the 2025 edition’s 2024 capacity
figure first, which my data-year rule counts as not relevant, with the 2026 chapter second, so that loss comes from near-identical editions, not lost context.
o17 and o22 each went from a rank-8 first hit to none in the top 10.

A 50-word overlap is a larger share of a 100-word chunk than of a 300-word one, so the change also altered how much neighboring chunks repeat. I did
not separate that from chunk size, so the mechanism in my hypothesis is untested.

---

## 6. Failure analysis

Pick the queries where your best system on your own corpus failed: the relevant document is missing from the top 10, or sits far below the top.
Take at least five, and read what the system returned next to what was relevant.
Then sort the failures by cause, for example a vocabulary mismatch, near-duplicate documents, a chunk that cut the answer in half, a query that is ambiguous, or a label that was wrong, because sometimes the gold set is what failed.

| qid | what the best system returned | what was relevant | cause | what you would try |
|---|---|---|---|---|
| o18 | `mcs2026-abrasives`, `mcs2025-abrasives`, `mcs2024-abrasives`, `mcs2026-sand-industrial`, `mcs2025-sand-industrial`, `mcs2026-diamond`, `mcs2025-diamond`, `mcs2024-diamond`, `mcs2026-iron-oxide-pigments`, `mcs2025-iron-oxide-pigments` | `mcs2024-garnet`, `mcs2025-garnet`, `mcs2026-garnet` | Vocabulary mismatch between the query and the garnet chapter (mcs2026-garnet), compounded by a candidate-pool cutoff. The query’s terms don’t appear in the chapter: “hard”, “red” and “grit” never occur, “waterjet cutting” is written “water-jet-assisted cutting” (a different token for bm25), and the end-use sentence says “abrasive blasting” rather than “sandblasting”, which appears only once, about 6,500 characters in, in the Substitutes paragraph. As a result, bm25 ranked the three garnet chapters 15-17 and dense ranked them 57, 60 and 82. Hybrid placed the best one at 21, one place outside the top 20 that rerank reorders, so rerank never saw garnet. | Don’t rename the query: o18 is a paraphrase query, and rewording it would hide the failure instead of fixing the system. Change the system instead, using my ablation as the lead: dense_small (100-word chunks) ranked the garnet chapters 1, 3 and 4 against dense’s 57, 60 and 82. Two options: 1. Use dense_small in hybrid in place of dense. 2. Raise rerank’s candidate pool from 20 to 30, which would have included garnet at rank 21. |
| o33 | `mcs2025-salt`, `mcs2026-salt`, `mcs2024-salt`, `mcs2024-magnesium-compounds`, `mcs2025-magnesium-metal`, `mcs2024-soda-ash`, `mcs2025-potash`, `mcs2026-potash`, `mcs2024-potash`, `mcs2025-bromine` | `mcs2026-salt` | The query is ambiguous about the year to the system even though the relevance rule protects against this. `mcs2025-salt` reports 2024 data but its title line says "Mineral Commodity Summaries 2025", while `mcs2026-salt` reports 2025 data. `bm25` had the right chapter at rank 1 so rerank moved a correct answer down. However, on the other four year queries (`o26`, `o27`, `o29`, `o35`), `rerank` put the correct 2026 chapter first, so this is not a general year problem. | One possible fix for this would be to tell the reranker in its prompt that a year in a query means the year the data describes. Then, `o33`'s first relevant rank should reach number 1 and the four other year queries (`o26`, `o27`, `o29`, `o35`) should keep rank 1. | 
| o05 | `mcs2026-rare-earths`, `mcs2026-rare-earths-heavy`, `mcs2026-yttrium`, `mcs2025-yttrium`, `mcs2024-yttrium`, `mcs2026-scandium`, `mcs2026-cobalt`, `mcs2025-cobalt`, `mcs2024-cobalt`, `mcs2024-tungsten` | `mcs2024-yttrium`, `mcs2025-yttrium`, `mcs2026-rare-earths-heavy`, `mcs2026-yttrium` | This is due to a label error since the yttrium chapters mention China and this is weighted unevenly since only the China part of the query is matched while the magnet part is not. The yttrium chapter lists ceramics and phosphors as its leading uses an dno magnet use. `mcs2026-rare-earths` has magnets as the leading use, neodymium-iron-boron magnet block, samarium-cobalt alloy, and 8 mentions of China. | I would use `mcs2026-rare-earths` and drop the yttrium chapters since yttrium doesn't have magnet use. Then I would re-judge o05 under my rule and report the corrected reciprocal rank separately from the frozen result (without editing `qrels.txt`). It would be expected that `rerank` put `mcs2026-rare-earths` at number 1, so the corrected reciprocal rank for o05 would be 1.0 instead of 0.5. |
| o17 | `mcs2026-niobium`, `mcs2025-niobium`, `mcs2024-niobium`, `mcs2026-tungsten`, `mcs2026-tin`, `mcs2024-thallium`, `mcs2026-rhenium`, `mcs2025-rhenium`, `mcs2024-rhenium`, `mcs2026-scandium`|`mcs2024-niobium`, `mcs2024-tantalum`, `mcs2025-niobium`, `mcs2025-tantalum`, `mcs2026-niobium`, `mcs2026-tantalum`| This could be due to a vocabulary mismatch since the "1950s" phrasing pertains to tantalum and niobium chapters when they mention the year 1959. This year vs decade phrasing gap applies to both elements, and `rerank` still found niobium at ranks 1 to 3. However, "steel" appears 5 times in the 2026 niobium chapter and once in tantalum. Since tantalum has fewer mentions of steel and superalloys, it fell below the cutoff. | It could be helpful to widen the potential candidate pool to the top 40. Then I would look to see if any of the tantalum chapters entered this top 40, and then again to see if any enter the top 10 after reranking and check that other queries keep their ranks, since a bigger pool can crowd out good results. |
| o22 | `mcs2026-beryllium`, `mcs2025-beryllium`, `mcs2024-beryllium`, `mcs2024-titanium`, `mcs2025-titanium`, `mcs2025-magnesium-metal`, `mcs2026-scandium`, `mcs2026-selenium`, `mcs2026-copper`, `mcs2025-copper` | `mcs2024-beryllium`,  `mcs2024-titanium`, `mcs2025-beryllium`,  `mcs2025-titanium`, `mcs2026-beryllium`,  `mcs2026-titanium` | `bm25` had `mcs2026-titanium` at rank 8, but `dense` didn’t have titanium in its top 10, so the fused score dropped below the cutoff. | It could be helpful to widen the potential candidate pool to the top 40. Then I would look to see if the chapter `mcs2026-titanium` entered this top 40, and then again to see if it enters the top 10 after reranking and check that other queries keep their ranks, since a bigger pool can crowd out good results. Additionally, I could give more weight to the `bm25` ranking so that `mcs2026-titanium` would rank higher, however, I could check that `mcs2026-titanium` enters hybrid’s top 20, and that paraphrase queries where dense helped don’t get worse. |
|---|---|---|---|---|

---

## 7. Cross-corpus comparison

The two tables to compare are the shared-corpus scores in section 1 and your own-corpus scores in section 4, with their intervals.
If you want them side by side, copy the rows you need into a table here and say that you copied them.

Did the winner change between the shared corpus and yours?
Why, or why not: what is different about the two collections (document length, vocabulary, identifiers, near-duplicates, how the queries were written), and which of your explanations did you test and which are guesses?
Say what 20 queries on one side and your gold-set size on the other cannot support.

TODO: write the cross-corpus comparison.

---

## 8. Stretch

498E: the stretch is one of the six options in the brief's "One stretch" section, and that section says what earns the 25 points for each.
It is optional, so `uv run p2 check --final` never waits on this section.
598E: the rider is your stretch, so write "rider" below and put its results in section 9; the other options add no points, because the project is capped at 150.

Whichever option you chose, write these five things:

1. The option's name.
2. What you did, and the files that hold it.
3. The table `p2 score` wrote for it, by name: one of the three below, `own-ablation` and `own-ablation-queries` in section 5 for a second ablation, `own-origins` in section 4 for the hand and claude queries, or `repeats` in section 9 for the rider.
4. What its interval lets you claim, and what it does not.
5. One thing you would do next, and what result would tell you it worked.

For a second ablation, write its hypothesis here before you run it, and commit it, so your history shows that it came first.
For the hand and claude queries, do the same with your prediction before you score.

### Claim-level faithfulness check (option 2)

Claude's verdicts from `p2 judge` against your own verdicts in the calibration file.

<!-- p2:begin stretch-judge -->
_No judged answers yet (stretch option 2): `uv run p2 judge answers/shared/LABEL.json` writes them, your own verdicts go in answers/shared/LABEL.calibration.tsv, and then `uv run p2 score` fills this table._
<!-- p2:end stretch-judge -->

### Cost and latency (option 3)

The Claude calls, tokens and seconds in every trace you committed, and what a cheaper system or answers file saves against what it loses.

<!-- p2:begin stretch-cost -->
Every trace in traces/ that records a Claude call:

| Trace | System | Spans | Claude calls | Saved | Input tokens | Output tokens | Seconds | Input per span | Output per span | Seconds per span |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| traces/answers-rerank.jsonl | rerank | 12 | 24 | 4 | 201,446 | 4,210 | 113.3 | 16,787 | 351 | 9.4 |
| traces/answers-rerank.r1.jsonl | rerank | 12 | 24 | 0 | 210,730 | 4,509 | 80.2 | 17,561 | 376 | 6.7 |
| traces/answers-rerank.r2.jsonl | rerank | 12 | 24 | 0 | 209,035 | 4,322 | 75.9 | 17,420 | 360 | 6.3 |
| traces/answers-rerank.r3.jsonl | rerank | 12 | 24 | 0 | 214,272 | 4,290 | 73.2 | 17,856 | 358 | 6.1 |
| traces/own-own-rerank.jsonl | rerank | 38 | 38 | 2 | 319,839 | 3,773 | 99.2 | 8,417 | 99 | 2.6 |
| traces/shared-practice-rerank.jsonl | rerank | 20 | 20 | 2 | 152,196 | 1,930 | 68.3 | 7,610 | 96 | 3.4 |
| traces/shared-practice-rerank.r1.jsonl | rerank | 20 | 20 | 0 | 170,173 | 2,040 | 53.4 | 8,509 | 102 | 2.7 |
| traces/shared-practice-rerank.r2.jsonl | rerank | 20 | 20 | 0 | 151,650 | 1,930 | 50.2 | 7,582 | 96 | 2.5 |
| traces/shared-practice-rerank.r3.jsonl | rerank | 20 | 20 | 0 | 161,438 | 2,040 | 50.9 | 8,072 | 102 | 2.5 |
| traces/shared-test-rerank.jsonl | rerank | 40 | 40 | 0 | 306,702 | 4,093 | 129.0 | 7,668 | 102 | 3.2 |

A span is one query of a run, one question of an answers file, or one claim of a judged file. A saved reply costs nothing now, so it counts the tokens and the seconds of the call that made it.

Every pair of systems on the same queries where at least one calls Claude, the one with fewer Claude input tokens per query first:

| Cheaper minus dearer | Queries | MRR@10 difference | 95% interval | Input tokens saved per query | Seconds saved per query | Reading |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| shared practice: bm25 minus rerank | 20 | -0.293 | [-0.533, -0.043] | 7,610 | 3.4 | rerank higher |
| shared practice: dense minus rerank | 20 | -0.237 | [-0.408, -0.083] | 7,610 | 3.4 | rerank higher |
| shared practice: hybrid minus rerank | 20 | -0.329 | [-0.504, -0.164] | 7,610 | 3.4 | rerank higher |
| own: bm25 minus rerank | 38 | -0.180 | [-0.292, -0.077] | 8,417 | 2.6 | rerank higher |
| own: dense minus rerank | 38 | -0.225 | [-0.359, -0.104] | 8,417 | 2.6 | rerank higher |
| own: hybrid minus rerank | 38 | -0.124 | [-0.232, -0.030] | 8,417 | 2.6 | rerank higher |

The difference is the cheaper system's score minus the dearer one's, with its paired interval; the savings count Claude calls only, so a system that makes none saves all of the other's.

Systems that do not call Claude, from traces/retrieval/ on the machine that last ran `p2 score` (git ignores that folder, so `p2 check` does not compare this part):

| Trace | System | Queries | Seconds | Milliseconds per query |
| --- | --- | ---: | ---: | ---: |
| traces/retrieval/own-own-ablation-dense_small.jsonl | dense_small | 38 | 0.12 | 3.1 |
| traces/retrieval/own-own-bm25.jsonl | bm25 | 38 | 0.01 | 0.4 |
| traces/retrieval/own-own-dense.jsonl | dense | 38 | 0.12 | 3.3 |
| traces/retrieval/own-own-hybrid.jsonl | hybrid | 38 | 0.12 | 3.2 |
| traces/retrieval/shared-practice-bm25.jsonl | bm25 | 20 | 0.02 | 1.1 |
| traces/retrieval/shared-practice-dense.jsonl | dense | 20 | 0.09 | 4.6 |
| traces/retrieval/shared-practice-hybrid.jsonl | hybrid | 20 | 0.13 | 6.5 |
| traces/retrieval/shared-test-bm25.jsonl | bm25 | 40 | 0.05 | 1.2 |
| traces/retrieval/shared-test-dense.jsonl | dense | 40 | 0.15 | 3.9 |
| traces/retrieval/shared-test-hybrid.jsonl | hybrid | 40 | 0.25 | 6.2 |
<!-- p2:end stretch-cost -->

### The grep agent (option 5)

Your stretch run on some of your own queries against the four systems on the same queries.

<!-- p2:begin stretch-agent -->
_No stretch runs yet (stretch option 5): `uv run p2 run --corpus own --queries eval/own/agent.queries.tsv --system agent --stretch` writes one to runs/own/stretch/, then `uv run p2 score` fills this table._
<!-- p2:end stretch-agent -->

### Your stretch

1. 598E rider

2. What you did, and the files that hold it.
  I ran three runs of rerank on the 20 shared practice queries and three sets of cited answers on the 12 shared questions and each of these times I asked Claude again. This is in commit d05a03d. The files are:
  - `runs/shared/rerank.practice.r1.trec` 
  - `runs/shared/rerank.practice.r2.trec`
  - `runs/shared/rerank.practice.r3.trec`
  - `answers/shared/rerank.r1.json`
  - `answers/shared/rerank.r2.json`
  - `answers/shared/rerank.r3.json`
  - `traces/shared-practice-rerank.r1.jsonl`
  - `traces/shared-practice-rerank.r2.jsonl`
  - `traces/shared-practice-rerank.r3.jsonl`
  - `traces/answers-rerank.r1.jsonl`
  - `traces/answers-rerank.r2.jsonl`
  - `traces/answers-rerank.r3.jsonl`
  - `results/results.json`

  The pre-registered claim is in `PREREG.md`, and the 38-query gold set is in `eval/own/qrels.txt`.

3. `repeats` in section 9 for the rider

4. The interval lets me claim:
    - the spread between runs is small: (range 0.025 on Recall@10, 0.000 on MRR@10, 0.013 on nDCG@10)
    - The gain of `rerank` over `hybrid` on the practice queries is larger than that spread and excludes zero in all three runs (MRR@10 +0.329 [+0.164, +0.504])

  The interval does not let me claim:
    - That the verified and declined shares are really 100%. The Wilson intervals are [0.676, 1.000] on 8 questions and [0.510, 1.000] on 4.
    - That the three repeats are independent trials. They use the same questions, so I did not pool them.
    - That the single own-corpus run of `rerank` would hold up across fresh Claude replies. On my corpus `rerank - hybrid` is +0.124 [+0.030, +0.232] on 38 queries, so `rerank` is distinguishably better there, but I repeated the reranker only on the shared corpus.
     - For the pre-registered claim: `hybrid - bm25` came out inconclusive, so it neither confirms nor rules out a gap of 0.15.

5. One thing I would do next is resolve the `hybrid - bm25` question. The MDD of 0.139 on 38 queries implies a spread of about 0.306. If the true gap is near +0.056, the upper end drops below 0.15 at about 41 queries, which is only a coin flip, and an 80% chance needs about 83. It worked if the interval has both ends inside ±0.15 (a well-powered null) or lies entirely above zero (supported). My pre-registration fixed n = 38, so the inconclusive result stands, and any extension would be a dated amendment in PREREG §6, not a rescue of this result.

---

## 9. 598E only - repeats and the pre-registered claim

498E students can leave this section as it is; nothing checks it.
598E students replace each line that starts with "598E: write", and `uv run p2 check --final` counts those lines as work still to do until they are gone.

### Repeats on the shared corpus

Three runs of the reranker on the practice queries, and three answers files, with their run-to-run spread and Wilson intervals.

<!-- p2:begin repeats -->
Repeated runs of rerank on shared/practice:

| Run | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| rerank.r1 | 0.758 | 0.800 | 0.755 |
| rerank.r2 | 0.733 | 0.800 | 0.750 |
| rerank.r3 | 0.758 | 0.800 | 0.763 |
| range (max minus min) | 0.025 | 0.000 | 0.013 |

| Comparison | Metric | Mean difference | 95% interval | Reading |
| --- | --- | ---: | ---: | --- |
| rerank.r1 minus hybrid | Recall@10 | +0.167 | [+0.058, +0.292] | rerank.r1 higher |
| rerank.r2 minus hybrid | Recall@10 | +0.142 | [+0.050, +0.258] | rerank.r2 higher |
| rerank.r3 minus hybrid | Recall@10 | +0.167 | [+0.058, +0.292] | rerank.r3 higher |
| rerank.r1 minus hybrid | MRR@10 | +0.329 | [+0.164, +0.504] | rerank.r1 higher |
| rerank.r2 minus hybrid | MRR@10 | +0.329 | [+0.164, +0.504] | rerank.r2 higher |
| rerank.r3 minus hybrid | MRR@10 | +0.329 | [+0.164, +0.504] | rerank.r3 higher |
| rerank.r1 minus hybrid | nDCG@10 | +0.312 | [+0.187, +0.440] | rerank.r1 higher |
| rerank.r2 minus hybrid | nDCG@10 | +0.306 | [+0.179, +0.437] | rerank.r2 higher |
| rerank.r3 minus hybrid | nDCG@10 | +0.320 | [+0.195, +0.448] | rerank.r3 higher |

Repeated answers shared/rerank:

| File | Verified (in) | 95% interval | Declined (out) | 95% interval |
| --- | ---: | ---: | ---: | ---: |
| rerank.r1 | 8 of 8 (100%) | [0.676, 1.000] | 4 of 4 (100%) | [0.510, 1.000] |
| rerank.r2 | 8 of 8 (100%) | [0.676, 1.000] | 4 of 4 (100%) | [0.510, 1.000] |
| rerank.r3 | 8 of 8 (100%) | [0.676, 1.000] | 4 of 4 (100%) | [0.510, 1.000] |
| range (max minus min) | 0.000 |  | 0.000 |  |

Each repeat answers the same questions, so the repeats are not independent trials and their counts are not pooled into one interval.
<!-- p2:end repeats -->

Does the reranker's gain over its first stage survive the run-to-run variation?
Write what the spread is, how it compares with the gain, and what the Wilson intervals on the verified share and the declined share say about 8 and 4 questions.

598E: write the repeats result here.

### The pre-registered claim

The claim, the smallest effect, the gold-set size and the test are in `PREREG.md`, committed before your own gold-set judgments.
Here, say whether you followed the plan, what the interval turned out to be, and what that means.
The outcome section of `PREREG.md` holds the short version.

598E: write the claim and its outcome here.
