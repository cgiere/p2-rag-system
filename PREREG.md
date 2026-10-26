# Pre-registration (598E)

This file is for 598E students; it is the second half of the 598E rider, and 498E students can ignore it or delete it.

A pre-registration is a claim you write down, with the test that will judge it, before you can see the answer.
Its value is that the claim can be wrong in a way anyone can check, and that you cannot adjust it afterwards to fit the numbers.
A well-powered result that says "no effect as large as the one I cared about" scores as well as a confirmation, so you have no reason to bend the claim.

**Git history is how I will know the order.**
Commit this file, filled in through section 4, before the first commit that puts a judgment line into `eval/own/qrels.txt` (or any other file under `eval/own/`).
`uv run p2 check` reads `git log` to find the first commit in which sections 1 to 4 have no TODO marker left and some words of yours in each, and confirms that it comes before your first judgment; a copy that was filled in afterwards fails.
Right after that commit, `p2 check` names it and waits for your first judgment; it asks for section 5 separately, once you have scored your own corpus.
You may ingest your corpus and write queries first, but not the relevance judgments.
After that first commit, do not edit sections 1 to 4, because `p2 check` compares them with the commit where you filled them in.
If something must change, add a dated entry in section 6 and leave the original as it was.

You need your stage 1 scores for section 3, so score the shared corpus first.

---

## 1. Hypothesis

One sentence, about your own corpus, naming two of your systems and a direction.
For example: "On my corpus of Kubernetes documentation, `rerank` has a higher MRR@10 than `hybrid`, because the queries are paraphrases that a first-stage fusion ranks too low."
It should be something you could be wrong about.

On my corpus of USGS Mineral Commodity Summaries, hybrid has a higher MRR@10 than bm25, because the queries mix exact
entities (commodity names, countries, years) with paraphrased descriptions of uses and trends (e.g. “metal used in EV
batteries” instead of “lithium”), and bm25 alone fails on the paraphrased ones.

---

## 2. The smallest effect that matters

Name one metric, MRR@10 or nDCG@10, and choose it now so you cannot pick the better one afterwards.
Then say how large a difference between the two systems would matter to a person using the search, and why that size.
A difference of 0.02 is usually not worth a reranker's cost in time and tokens.
In this course, choose a Δ of at least 0.15 unless you argue for a larger one, because a smaller gap takes more queries than one project can judge.
Call your number Δ (delta).

Metric: MRR@10. I am choosing it now, before running any system.

Δ = 0.15. A user asking a question of the USGS Mineral Commodity Summaries wants one passage that answers it, such as a
production figure, an import-reliance percentage, or a trend statement. MRR@10 is a direct fit for that: it measures how
far down the list they must read before reaching an answer. A gain of 0.15 is roughly the difference between the first
correct passage landing around rank 3 versus rank 2 on a typical query (reciprocal rank 0.33 vs. 0.50), or between a
correct passage appearing in the top 10 for a noticeably larger share of queries. A user would feel that as less scrolling
and fewer reformulated searches. A gain of 0.02 would be invisible to a person, and it would not justify the added
complexity of running a second retriever and fusing the results. From my sample-size table, detecting Δ = 0.15 for hybrid -
bm25 on MRR@10 (sd = 0.307) needs about 33 queries, which is feasible for this project.

---

## 3. How many queries you need

The size of the gold set follows from three numbers: how large a difference you want to detect (Δ), how variable the per-query differences are (sd), and the usual choices of a 5% false-alarm rate and 80% power.

```
n = ((1.96 + 0.84) * sd / Δ)^2
```

Here sd is the standard deviation of the per-query differences between your two systems, which `results/results.json` holds for the shared practice queries.
Compute it from your stage 1 runs for the same two systems, or the nearest pair you have, and say which pair you used.
With only 20 practice queries the sd is itself noisy, so be generous and round up.

Some numbers to calibrate against.
At sd 0.3 and Δ 0.10 the formula gives about 71 queries, and with the t distribution's small-sample correction it is a few more, about 73.
At sd 0.3, a gold set of 30 queries can only detect a difference of about 0.15, which is why 30 queries cannot support a claim about a gap of 0.10.
The spreads you will measure on the shared practice queries are mostly larger than 0.3: from about 0.31 for `hybrid` against `bm25` to about 0.66 for `dense` against `bm25`.
For `rerank` against `hybrid` the sd is about 0.39, so a Δ of 0.10 needs about 120 queries, 0.15 about 55, and 0.20 about 31.
So the course's Δ of 0.15 means about 55 queries for that pair; at an sd of 0.66 it would mean about 150, so compare a pair whose spread you can afford.
Choose Δ and the size of your gold set together: the smallest effect that matters to a user, and a number of queries you can write and judge in the time you have.
If the two do not meet, say which one you gave ground on and why.

After you score the own corpus, the minimum detectable difference that `uv run p2 score` prints for your two systems is this same calculation run the other way.
It should come out at or below your Δ.
If it does not, your queries varied more than your stage 1 sd suggested, and you will say so in the outcome.

sd: 0.307, the standard deviation of the per-query MRR@10 difference between hybrid and bm25 on the 20 shared practice
queries (from results/results.json, stage 1 runs).

Δ: 0.15, from section 2.

n: ((1.96 + 0.84) x 0.307 / 0.15)^2 = 32.8, so 33 queries

I will write at least n queries (38 queries). The measured sd for hybrid vs bm25 on MRR@10 is 0.307, which gives n = 33. 
Because that sd comes from only 20 practice queries, we pad it up to 0.33 (about 7% higher). 
Using 0.33 for sd gives us: n = ((1.96 + 0.84) x 0.330 / 0.15)^2 = 37.9 or 38 queries. 

---

## 4. The test, and what each result will mean

The test is the paired 95% interval of the mean difference between your two systems on your own gold set, from the `own-pairs` table that `uv run p2 score` writes in `EVAL.md`.
Write the rule now.
This is the default rule, and you can tighten it, but do not loosen it after you see your numbers.

| The interval is | I will say |
|---|---|
| entirely above zero in the direction I predicted | supported: the difference is distinguishable from zero |
| entirely on the other side of zero | contradicted: the opposite of my hypothesis holds on this gold set |
| around zero, with both ends inside plus or minus Δ | well-powered null: a difference as large as Δ is ruled out |
| around zero, with an end beyond plus or minus Δ | inconclusive: the gold set could not settle it, and I say so |


Systems and metric: hybrid vs bm25 on MRR@10, difference = hybrid − bm25, predicted direction positive. Δ = 0.15.

Rule: I keep the default four-row rule exactly as written. I fixed it before scoring and will not loosen it afterwards.

One clarification: if the interval is entirely above zero, I will report “supported” per row 1, and I will also
report the point estimate and the interval next to Δ = 0.15, so the reader can see whether the effect is as large as the
one I said would matter.

---

## 5. Outcome (write this after the fact)

What was the interval?
Which row of the table in section 4 is it?
Did your gold set reach the size section 3 asked for, and what was the minimum detectable difference that `uv run p2 score` printed?
What would you do next, and what would you want a reader to take from this?

On my 38-query gold set, hybrid scored +0.056 above bm25 on MRR@10 (95% interval −0.039 to +0.153). The interval includes zero and its upper end exceeds my Δ of 
0.15, so under my pre-stated rule the result is inconclusive: I cannot rule out a difference as large as 0.15, nor show one. The minimum detectable difference
was 0.139, below my Δ, so the set was as sensitive as planned.

---

## 6. Amendments

Dated entries only, one per change, each saying what changed and why.
Leave this section as it is if nothing changed.
