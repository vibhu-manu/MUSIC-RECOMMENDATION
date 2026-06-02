from __future__ import annotations
from typing import List, Tuple
import numpy as np
from backend.app.recommender.catalog import Song


class RetrievalEngine:
    def __init__(self, songs: List[Song]):
        self.songs = songs
        self.matrix = np.array([song.embedding for song in songs], dtype=np.float32)
        self.index = None
        try:
            import faiss

            self.index = faiss.IndexFlatIP(self.matrix.shape[1])
            self.index.add(self.matrix)
        except Exception:
            self.index = None

    def search(self, query_embedding: List[float], k: int) -> List[Tuple[Song, float]]:
        if len(self.songs) == 0:
            return []
        query = np.array([query_embedding], dtype=np.float32)
        if self.index is not None:
            scores, indices = self.index.search(query, min(k, len(self.songs)))
            return [(self.songs[int(index)], float(score)) for index, score in zip(indices[0], scores[0]) if index >= 0]
        scores = np.dot(self.matrix, query[0])
        indices = np.argsort(scores)[::-1][:k]
        return [(self.songs[int(index)], float(scores[int(index)])) for index in indices]
