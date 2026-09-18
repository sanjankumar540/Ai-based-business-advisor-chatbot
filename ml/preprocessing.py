"""
ml/preprocessing.py
--------------------
Shared preprocessing helpers for the business-risk dataset so that
train_model.py and predict.py always encode categorical features the
same way.
"""

import pandas as pd

CATEGORICAL_COLUMNS = ["business_type", "market_demand", "competition", "experience", "target_market"]
NUMERIC_COLUMNS = ["investment", "operating_cost"]
FEATURE_COLUMNS = ["business_type", "investment", "market_demand", "competition",
                    "experience", "operating_cost", "target_market"]
TARGET_COLUMN = "risk_level"


def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.dropna()
    return df


def encode_features(df: pd.DataFrame, encoders: dict, fit: bool = False):
    """
    Encodes categorical columns using sklearn LabelEncoders stored in `encoders`.
    If fit=True, fits new encoders on df (used during training).
    If fit=False, reuses previously-fitted encoders (used during prediction).
    Returns a new DataFrame with categorical columns replaced by integer codes.
    """
    from sklearn.preprocessing import LabelEncoder

    df = df.copy()
    for col in CATEGORICAL_COLUMNS:
        if fit:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            le = encoders[col]
            # handle unseen categories gracefully by mapping to the most common class
            df[col] = df[col].astype(str).apply(
                lambda v: v if v in le.classes_ else le.classes_[0]
            )
            df[col] = le.transform(df[col])
    return df, encoders
