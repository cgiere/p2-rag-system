# Decision log

Your methods section, in your own words.
About one to two pages in total.

Answer these as you go, not the night before it is due.
Each answer is easier to write while the decision is still fresh, and prompt 1 only works if you write it before you see your own-corpus numbers.
Specifics beat polish: a short, honest answer with a number in it is worth more than a long vague one.

Each prompt ends with a marker line.
Replace that line with your answer.
`uv run p2 check` reports a marker as unfinished work, and `uv run p2 check --final` fails while any marker is left, so a finished log is part of being done.

Please do not let the agent write these for you.
These answers are about what you chose and what you knew, and the agent cannot know that.
Prompt 3 in particular only works in your own words.

---

## 1. Why this corpus, and what you expected

Why did you pick the corpus you used in stage 2, and why does it belong to a field or a question you care about?
Then say what you expected before you measured anything: which of `bm25`, `dense`, `hybrid` and `rerank` do you think will win on it, and which will do worst, and why?

Commit this answer before your first `uv run p2 score` on the own corpus.
Git history then shows that the expectation came first, which is what lets it be wrong in a way that teaches you something.
If you were surprised later, say so in prompt 4 or in EVAL.md; do not come back and rewrite this one.

The corpus I chose was USGS Mineral Commodity Summaries since I thought it would be meaningful to an examine an analysis of the critical minerals industry using a RAG system since this field that is so closely intertwined with Colorado School of Mines. I think the `hybrid` will have the best performance since it combines `dense` and `bm25` so it can therefore get matches from keywords and meaning. I think `bm25` will have the worst performance since it is just a classic keyword search.

---

## 2. A fork in the road

Name one real design choice where you could have gone two ways: the chunk size, the embedding model, how the two systems are fused, how many documents the reranker sees, a sentence in `prompts/answer.txt`, how you cleaned the corpus.

Say which you picked, what the alternative was, and what you gave up by not taking it.
If you measured both, give both numbers.
If you rejected the alternative without measuring it, say why that was a fair call, and what it cost you in time, tokens or complexity.

"There was no alternative" is not an answer.
Find the fork.

A fork in the road was choosing the 300-word chunks for all four systems (`chunking` in `p2.toml`). The alternative, 100-word chunks, was tested in the `dense_small` ablation. The results from the ablation show that the 100-word version scored higher: `dense` is 0.722 MRR@10 and `dense_small` is 0.798, but the difference of +0.076, [-0.029, +0.185] is not distinguishable. However, the overlap stayed at 50 words, which is a larger share of a 100-word chunk, so the ablation changed more than chunk size. The ablation changed only `dense`. `bm25` and `hybrid` still use 300-word chunks, so it does not show how the 100-word chunks would affect them. By keeping 300 words I gave up a possible small gain for dense, which I can’t confirm because the interval includes zero.

---

## 3. Where you overruled the agent

One time Claude suggested, wrote or claimed something and you did not take it.
It might be a relevance judgment you disagreed with, a retriever it called finished when a run file showed otherwise, a number it summarized wrongly, or a license it said was fine.

What did it do?
How did you notice?
What did you do instead?

If it genuinely never happened, say so plainly, and then say what you would have had to check in order to notice.
Being honest here costs you far less than a story you cannot defend when you record your video.

I did not overrule the agent at any juncture. Claude drafted 28 of the queries, but I made every relevance judgment myself. To notice a bad suggestion I would have had to compare the pool of 818 candidates Claude built with what I found reading the chapters.

---

## 4. A number you do not trust

Pick one number in `EVAL.md` that you do not fully trust, and say why.
It could be a mean over a small query class, a difference whose interval includes zero, a verified share of 100%, a score on a gold set you wrote yourself, or a result you got only once.

What would have to be true for you to trust it?
Did you do anything to test it, and what did that show?

A number that I don't trust is `rerank`’s own-corpus MRR@10 of 0.947, from one run, since I repeated the reranker only on the shared corpus. The margin is narrow: `rerank` minus `hybrid` on MRR@10 is +0.124, [+0.030, +0.232]. The lower end is barely above zero, so a different Claude reply on a few queries could shrink it, but I did not measure that on my corpus. I would trust it if repeated runs on my corpus showed a small range, as they did on the shared corpus. On the shared corpus, three repeats gave an MRR@10 range of 0.000, and no query’s first relevant rank moved. On my corpus I did not repeat it, so I did not test this number directly. The shared result doesn’t prove the same for mine.

---

## 5. What is still wrong

One thing in your system, your corpus or your gold set that is not right, not finished, or that you do not fully understand.

What would you do next, and how would you find out whether it matters?
Name the file, the query or the document where someone could look.

I found relevant chapters by grepping the commodity, country and year and then skimmed the chapters to see if they answered the queries. If there was a relevant chapter that I didn't grep for then this would be unlabeled and therefore counted against every system. An example is `o05`: `mcs2026-rare-earths` says magnets were the leading use and names neodymium-iron-boron, but the chapter is not in `qrels.txt`. The candidate list had 818 chapters (about 21.5 per query), and I labeled 120 as relevant, so I didn’t read all the rest in full. Next I would reread the unlabeled chapters in `rerank`’s top 5 for a sample of queries (the 10 failure queries or the paraphrase queries) and decide under my rule whether any is relevant. I would report corrected scores separately from the frozen ones, without editing `qrels.txt`. If the corrected MRR@10 moves by more than the `rerank` margin over `hybrid` (+0.124), the labeling affected my conclusions. Someone could find this in `eval/own/qrels.txt`.
