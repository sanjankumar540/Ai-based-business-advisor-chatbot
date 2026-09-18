"""
ml/predict.py
-------------
Loads the trained Random Forest model + encoders and predicts business
risk for a single new input. Used by routes/prediction.py, and can also
be run standalone for a quick command-line test:

    python ml/predict.py
"""

import os
import sys
import pickle
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Config
from ml.preprocessing import encode_features, FEATURE_COLUMNS


class ModelNotTrainedError(Exception):
    pass


def _load_artifacts():
    if not os.path.exists(Config.MODEL_PATH) or not os.path.exists(Config.ENCODERS_PATH):
        raise ModelNotTrainedError(
            "Model not found. Please run 'python ml/train_model.py' first."
        )
    with open(Config.MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(Config.ENCODERS_PATH, "rb") as f:
        encoders = pickle.load(f)
    return model, encoders


def predict_risk(business_type: str, investment: float, market_demand: str,
                  competition: str, experience: str, operating_cost: float,
                  target_market: str) -> dict:
    """
    Returns:
        {
            "predicted_risk": "Low Risk" | "Medium Risk" | "High Risk",
            "probabilities": {"Low Risk": 0.12, "Medium Risk": 0.55, "High Risk": 0.33}
        }
    Raises ModelNotTrainedError if the model hasn't been trained yet
    (caller should catch this and show a friendly error / prompt to train).
    """
    model, encoders = _load_artifacts()

    input_df = pd.DataFrame([{
        "business_type": business_type,
        "investment": investment,
        "market_demand": market_demand,
        "competition": competition,
        "experience": experience,
        "operating_cost": operating_cost,
        "target_market": target_market,
    }])

    encoded_df, _ = encode_features(input_df, encoders, fit=False)
    X = encoded_df[FEATURE_COLUMNS]

    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    class_labels = model.classes_

    prob_dict = {label: round(float(prob), 4) for label, prob in zip(class_labels, probabilities)}

    return {
        "predicted_risk": prediction,
        "probabilities": prob_dict,
    }


# Domain-knowledge direction map: for each feature, which raw values push
# risk UP. Used to combine the model's global feature importance with the
# direction of THIS specific input, producing a per-prediction explanation
# rather than a single static ranking every time.
_RISK_INCREASING_VALUES = {
    "market_demand": {"Low": True, "Medium": False, "High": False},
    "competition": {"Low": False, "Medium": False, "High": True},
    "experience": {"Low": True, "Medium": False, "High": False},
    "target_market": {"Small": True, "Medium": False, "Large": False},
}


def explain_prediction(business_type: str, investment: float, market_demand: str,
                        competition: str, experience: str, operating_cost: float,
                        target_market: str, top_n: int = 5) -> list:
    """
    Returns a list of risk-factor explanations, ranked by the trained
    Random Forest's global feature importances, each tagged with whether
    THIS specific input pushes risk up or down for that feature:

        [{"feature": "competition", "impact": "HIGH", "direction": "increases risk",
          "value": "High"}, ...]

    This is a transparent combination of (a) real model feature importances
    (model.feature_importances_) and (b) simple domain-knowledge direction
    rules for the categorical fields — not a black box, and explainable in
    a viva as: "the model tells us which features matter most overall; we
    show whether this user's specific value for that feature is favorable
    or unfavorable."
    """
    model, _ = _load_artifacts()
    importances = model.feature_importances_  # aligned with FEATURE_COLUMNS order

    input_values = {
        "business_type": business_type, "investment": investment,
        "market_demand": market_demand, "competition": competition,
        "experience": experience, "operating_cost": operating_cost,
        "target_market": target_market,
    }

    ranked = sorted(zip(FEATURE_COLUMNS, importances), key=lambda x: x[1], reverse=True)

    explanations = []
    for feature, importance in ranked[:top_n]:
        value = input_values[feature]

        if feature in _RISK_INCREASING_VALUES:
            increases_risk = _RISK_INCREASING_VALUES[feature].get(value, False)
            direction = "increases risk" if increases_risk else "reduces risk"
        elif feature == "investment":
            direction = "increases risk" if investment >= 750000 else (
                "neutral" if investment >= 200000 else "reduces risk"
            )
        elif feature == "operating_cost":
            direction = "increases risk" if operating_cost >= investment * 0.2 else "reduces risk"
        else:
            direction = "neutral"

        if importance >= 0.20:
            impact = "HIGH"
        elif importance >= 0.10:
            impact = "MEDIUM"
        else:
            impact = "LOW"

        explanations.append({
            "feature": feature.replace("_", " ").title(),
            "value": value,
            "impact": impact,
            "direction": direction,
            "importance_pct": round(float(importance) * 100, 1),
        })

    return explanations


if __name__ == "__main__":
    # quick manual test
    result = predict_risk(
        business_type="Fashion & Clothing",
        investment=300000,
        market_demand="High",
        competition="Medium",
        experience="Low",
        operating_cost=45000,
        target_market="Medium",
    )
    print(result)
