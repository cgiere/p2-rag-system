"""Reranking (stage 1): ask Claude to reorder a first-stage system's top 20.

It is rerank_one() of the 13 lab's pipeline.py:
- the first stage's top 20 go to Claude as numbered passages, each document cut to its first 600
  characters (its title line comes first, so the section number and heading are always in it);
- RERANK_SCHEMA forces the reply into {"order": [20 numbers]}, each between 1 and 20;
- a reply that is not each number once, or a failed call, keeps the first-stage order;
- the documents below the 20 keep their first-stage order underneath.
The first stage, the number of candidates and the passage length are [rerank] in p2.toml.
A document's score is 1 / its new rank, so scores fall as ranks rise.

search_chunks does the same over the first stage's top chunks, with each chunk's whole text, for
`p2 answer --system rerank`.

Every call goes through p2.claude.call, which caches the reply in .cache/claude/ and records the
tokens in the trace that p2 run writes next to the run file (commit both).
"""

from __future__ import annotations

from p2 import claude, retrievers

NEEDS_CLAUDE = True

RERANK_PROMPT = """Below are {n} passages from a document collection, numbered 1 to {n}, and a search query.
Order the passages from the most useful for answering the query to the least useful.
Reply with all {n} passage numbers, each exactly once, best first.

Query: {query}

{passages}"""


def schema(n):
    item = {"type": "integer", "minimum": 1, "maximum": n}
    return {
        "type": "object",
        "properties": {"order": {"type": "array", "items": item, "minItems": n, "maxItems": n}},
        "required": ["order"],
    }


class Rerank:
    def __init__(self, corpus, cfg):
        settings = cfg.table("rerank")
        self.cfg = cfg
        self.first = retrievers.build(settings.get("first_stage", "hybrid"), corpus, cfg)
        self.candidates = settings.get("candidates", 20)
        self.passage_chars = settings.get("passage_chars", 600)
        self.doc_texts = {d: doc.text[: self.passage_chars] for d, doc in corpus.docs.items()}
        self.chunk_texts = corpus.chunk_texts(cfg.chunk_words, cfg.chunk_overlap)
        self.model = cfg.model

    def rerank(self, query, ranking, texts):
        """The ids of `ranking` with its top candidates in Claude's order, the rest as they were."""
        ids = [i for i, _ in ranking]
        top, rest = ids[: self.candidates], ids[self.candidates :]
        if len(top) < 2:
            return ids
        passages = "\n\n".join(f"[{n}] {texts[i]}" for n, i in enumerate(top, 1))
        prompt = RERANK_PROMPT.format(n=len(top), query=query, passages=passages)
        reply = claude.call(prompt, schema(len(top)), model=self.cfg.model, cache_dir=claude.cache_folder(self.cfg))
        order = (reply.output or {}).get("order")
        if reply.error or not isinstance(order, list) or sorted(order) != list(range(1, len(top) + 1)):
            return ids  # an unusable reply keeps the first-stage order
        return [top[n - 1] for n in order] + rest

    def search(self, text, k):
        ranking = self.first.search(text, max(k, self.candidates))
        return [(d, 1 / r) for r, d in enumerate(self.rerank(text, ranking, self.doc_texts), 1)][:k]

    def search_chunks(self, text, k):
        ranking = self.first.search_chunks(text, max(k, self.candidates))
        return [(c, 1 / r) for r, c in enumerate(self.rerank(text, ranking, self.chunk_texts), 1)][:k]


def build(corpus, cfg):
    return Rerank(corpus, cfg)
