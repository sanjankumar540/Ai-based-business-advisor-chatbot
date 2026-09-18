"""
tests/test_ml.py - ML prediction sanity checks.
Requires ml/model.pkl to already exist (run `python ml/train_model.py` first).
"""

import pytest
from ml.predict import predict_risk, ModelNotTrainedError


def test_predict_risk_returns_valid_label():
    try:
        result = predict_risk(
            business_type="Retail", investment=100000, market_demand="High",
            competition="Low", experience="High", operating_cost=10000,
            target_market="Medium",
        )
    except ModelNotTrainedError:
        pytest.skip("Model not trained yet — run ml/train_model.py first.")
        return

    assert result["predicted_risk"] in ["Low Risk", "Medium Risk", "High Risk"]
    assert sum(result["probabilities"].values()) == pytest.approx(1.0, abs=0.01)


def test_predict_risk_handles_unseen_business_type_gracefully():
    try:
        result = predict_risk(
            business_type="Some Totally New Category", investment=50000,
            market_demand="Medium", competition="Medium", experience="Medium",
            operating_cost=5000, target_market="Small",
        )
    except ModelNotTrainedError:
        pytest.skip("Model not trained yet — run ml/train_model.py first.")
        return

    assert result["predicted_risk"] in ["Low Risk", "Medium Risk", "High Risk"]
