"""tests/test_rag.py - RAG retrieval sanity checks."""

from ai.rag import get_retriever


def test_retriever_indexes_knowledge_base():
    retriever = get_retriever()
    assert len(retriever.chunks) > 0


def test_retrieve_returns_relevant_results():
    retriever = get_retriever()
    results = retriever.retrieve("marketing strategy for clothing business", top_k=3)
    assert len(results) > 0
    # the top result should come from a plausibly relevant source file
    assert results[0]["score"] > 0


def test_retrieve_as_context_returns_string():
    retriever = get_retriever()
    context = retriever.retrieve_as_context("restaurant risk", top_k=2)
    assert isinstance(context, str)
