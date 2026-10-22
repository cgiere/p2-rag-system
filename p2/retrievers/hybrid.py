"""Hybrid retrieval (stage 1): reciprocal rank fusion of two systems, bm25 and dense by default.

It is rrf() of the 13 lab's pipeline.py: a document scores the sum of 1 / (k + rank) over the
rankings, with k = 60 and rank counted from 1.
- the fused systems and k are [hybrid] systems and rrf_k in p2.toml;
- each system is built through p2.retrievers.build, so its index is built once per run;
- each system ranks every document (every chunk for search_chunks), not just its top k, so a
  document that is 11th in both lists can still reach the fused top 10;
- the fused list is ordered with p2.runfile.order, so equal scores fall in id order.
"""

from __future__ import annotations

from collections import defaultdict

from p2 import retrievers
from p2.runfile import order

NEEDS_CLAUDE = False


def rrf(rankings, k):
    """Reciprocal rank fusion of rankings given as [(id, score), ...] best first."""
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, (item, _score) in enumerate(ranking, 1):
            scores[item] += 1 / (k + rank)
    return order(scores.items())


class Hybrid:
    def __init__(self, corpus, cfg):
        settings = cfg.table("hybrid")
        names = settings.get("systems", ["bm25", "dense"])
        self.k = settings.get("rrf_k", 60)
        self.systems = [retrievers.build(name, corpus, cfg) for name in names]
        self.n_docs = len(corpus.docs)
        self.model = next((s.model for s in self.systems if getattr(s, "model", None)), None)

    def search(self, text, k):
        return rrf([s.search(text, self.n_docs) for s in self.systems], self.k)[:k]

    def search_chunks(self, text, k):
        return rrf([s.search_chunks(text, len(s.chunks)) for s in self.systems], self.k)[:k]


def build(corpus, cfg):
    return Hybrid(corpus, cfg)
