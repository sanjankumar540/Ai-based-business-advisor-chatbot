"""tests/test_idea_generator.py - Business Idea Generator sanity checks."""

import pytest
from ml.idea_generator import generate_ideas
from ml.predict import ModelNotTrainedError


def test_generate_ideas_respects_budget():
    try:
        ideas = generate_ideas(budget=100000, top_n=4)
    except ModelNotTrainedError:
        pytest.skip("Model not trained yet — run ml/train_model.py first.")
        return
    assert len(ideas) > 0
    for idea in ideas:
        assert idea["investment"] <= 100000 * 1.15


def test_generate_ideas_returns_structured_fields():
    try:
        ideas = generate_ideas(budget=300000, keywords=["food"], top_n=3)
    except ModelNotTrainedError:
        pytest.skip("Model not trained yet — run ml/train_model.py first.")
        return
    for idea in ideas:
        assert "name" in idea
        assert "investment" in idea
        assert "predicted_risk" in idea
        assert "potential" in idea


def test_generate_ideas_handles_tiny_budget_gracefully():
    try:
        ideas = generate_ideas(budget=5000, top_n=4)
    except ModelNotTrainedError:
        pytest.skip("Model not trained yet — run ml/train_model.py first.")
        return
    assert len(ideas) > 0  # falls back to cheapest options instead of returning nothing
