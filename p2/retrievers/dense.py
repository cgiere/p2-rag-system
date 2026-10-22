"""Dense retrieval (stage 1): embed every chunk once, embed the query, and rank chunks by cosine similarity.

It is the bge arm of the 12 lab's retrieve.py (dense_rankings) moved onto chunks:
- the model is [dense] model in p2.toml, bge-small-en-v1.5 by default, loaded with embed.load;
- embed.doc_vectors encodes the chunks once and caches them in .cache/vectors/;
- every vector has length 1, so the dot product of the query vector with a chunk's vector is their
  cosine similarity, and one matrix product scores every chunk.
The query is embedded as it is, with no instruction prefix, as in the lab's plain bge arm.
ChunkScorer lifts the chunk scores to documents (a document scores its best chunk).
"""

from __future__ import annotations

import numpy as np

from p2 import embed
from p2.retrievers import ChunkScorer

NEEDS_CLAUDE = False


class Dense(ChunkScorer):
    def __init__(self, corpus, cfg):
        super().__init__(corpus, cfg)
        self.model = cfg.table("dense").get("model", embed.BGE)
        self.embedder = embed.load(self.model)
        self.vectors = embed.doc_vectors(self.embedder, [c.text for c in self.chunks], cfg.root)

    def score_chunks(self, text: str) -> np.ndarray:
        if not len(self.chunks):
            return np.zeros(0, dtype=np.float32)
        query = self.embedder.encode([text])[0]
        return self.vectors @ query


def build(corpus, cfg):
    return Dense(corpus, cfg)
