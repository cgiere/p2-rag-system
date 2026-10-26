"""Ablation of dense: the same model and scoring, over 100-word chunks instead of [chunking] words.

Only the chunk size changes:
- chunks are 100 words, with the same overlap as [chunking] in p2.toml (50 words);
- the model, embed.doc_vectors (cached in .cache/vectors/) and the dot-product scoring are Dense's;
- a document still scores its best chunk.
"""

from __future__ import annotations

from p2 import embed
from p2.retrievers import ChunkScorer
from p2.retrievers.dense import Dense

NEEDS_CLAUDE = False
BASE = "dense"

CHUNK_WORDS = 100


class DenseSmall(Dense):
    def __init__(self, corpus, cfg):
        ChunkScorer.__init__(self, corpus, cfg)
        self.chunks = corpus.chunks(CHUNK_WORDS, cfg.chunk_overlap)
        self.model = cfg.table("dense").get("model", embed.BGE)
        self.embedder = embed.load(self.model)
        self.vectors = embed.doc_vectors(self.embedder, [c.text for c in self.chunks], cfg.root)


def build(corpus, cfg):
    return DenseSmall(corpus, cfg)
