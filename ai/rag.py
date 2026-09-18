"""
ai/rag.py
---------
A genuine (not faked) Retrieval-Augmented Generation retriever.

How it works:
    1. On startup, every .txt file inside knowledge_base/ is loaded and
       split into paragraph-sized "chunks".
    2. All chunks are vectorized with TF-IDF (scikit-learn).
    3. At query time, the user's question is vectorized with the same
       fitted vectorizer, and cosine similarity is computed against every
       chunk.
    4. The top-k most similar chunks are returned as "retrieved context".

This is intentionally simple (no external vector database) so it is easy
to explain in a viva, while still being a real retrieval system: the
returned context genuinely changes based on the query.
"""

import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import Config


class KnowledgeBaseRetriever:
    def __init__(self, kb_dir: str = None):
        self.kb_dir = kb_dir or Config.KNOWLEDGE_BASE_DIR
        self.chunks = []          # list[str]
        self.sources = []         # list[str] (filename each chunk came from)
        self.vectorizer = None
        self.doc_matrix = None
        self._build_index()

    def _load_documents(self):
        chunks, sources = [], []
        pattern = os.path.join(self.kb_dir, "*.txt")
        for filepath in sorted(glob.glob(pattern)):
            filename = os.path.basename(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            # split on blank lines -> paragraphs (chunks)
            raw_chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
            for c in raw_chunks:
                chunks.append(c)
                sources.append(filename)
        return chunks, sources

    def _build_index(self):
        self.chunks, self.sources = self._load_documents()
        if not self.chunks:
            # No knowledge base files found - keep retriever safely empty
            self.vectorizer = None
            self.doc_matrix = None
            return
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = self.vectorizer.fit_transform(self.chunks)

    def retrieve(self, query: str, top_k: int = 3) -> list:
        """
        Returns a list of dicts: [{"text": ..., "source": ..., "score": ...}, ...]
        ordered by relevance (highest similarity first).
        """
        if not self.chunks or self.vectorizer is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.doc_matrix).flatten()

        # rank chunk indices by similarity, descending
        ranked_indices = similarities.argsort()[::-1][:top_k]

        results = []
        for idx in ranked_indices:
            score = float(similarities[idx])
            if score <= 0:
                continue  # don't return completely irrelevant chunks
            results.append({
                "text": self.chunks[idx],
                "source": self.sources[idx],
                "score": round(score, 4),
            })
        return results

    def retrieve_as_context(self, query: str, top_k: int = 3) -> str:
        """Flatten retrieved chunks into a single context string for the LLM prompt."""
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return ""
        parts = []
        for r in results:
            parts.append(f"[Source: {r['source']}]\n{r['text']}")
        return "\n\n".join(parts)


# Module-level singleton so the knowledge base is indexed only once per process
_retriever_instance = None


def get_retriever() -> KnowledgeBaseRetriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = KnowledgeBaseRetriever()
    return _retriever_instance
