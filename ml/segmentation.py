"""
ml/segmentation.py
-------------------
Customer segmentation using K-Means clustering (scikit-learn) on
data/customer_dataset.csv.

Clusters are labeled by average spending amount (ascending) as:
    Budget Customers < Regular Customers < Premium Customers < High-Value Customers

Run standalone with:
    python -m ml.segmentation
"""

import os
import sys
import pickle
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import Config

SEGMENT_LABELS_BY_RANK = ["Budget Customers", "Regular Customers", "Premium Customers", "High-Value Customers"]
FEATURES = ["age", "income", "purchase_frequency", "spending_amount"]


def train_segmentation_model(n_clusters: int = 4):
    dataset_path = os.path.join(Config.DATA_DIR, "customer_dataset.csv")
    df = pd.read_csv(dataset_path).dropna()

    X = df[FEATURES]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_ids = kmeans.fit_predict(X_scaled)

    df["cluster"] = cluster_ids

    # Rank clusters by mean spending_amount (ascending) and map to friendly labels
    cluster_order = (
        df.groupby("cluster")["spending_amount"].mean().sort_values().index.tolist()
    )
    cluster_to_label = {
        cluster_id: SEGMENT_LABELS_BY_RANK[rank]
        for rank, cluster_id in enumerate(cluster_order)
    }
    df["segment"] = df["cluster"].map(cluster_to_label)

    # Save model artifacts
    os.makedirs(Config.ML_DIR, exist_ok=True)
    with open(Config.SEGMENTATION_MODEL_PATH, "wb") as f:
        pickle.dump({"kmeans": kmeans, "scaler": scaler, "cluster_to_label": cluster_to_label}, f)

    return df


def load_segmentation_artifacts():
    if not os.path.exists(Config.SEGMENTATION_MODEL_PATH):
        return None
    with open(Config.SEGMENTATION_MODEL_PATH, "rb") as f:
        return pickle.load(f)


def get_segment_summary() -> dict:
    """
    Returns a summary suitable for the dashboard/analytics page:
    {
        "segments": {"Budget Customers": 90, "Regular Customers": 105, ...},
        "cluster_stats": [{"segment": ..., "avg_income": ..., "avg_spending": ...}, ...]
    }
    Trains the model on first call if it hasn't been trained yet.
    """
    artifacts = load_segmentation_artifacts()
    dataset_path = os.path.join(Config.DATA_DIR, "customer_dataset.csv")

    if artifacts is None:
        df = train_segmentation_model()
    else:
        df = pd.read_csv(dataset_path).dropna()
        X_scaled = artifacts["scaler"].transform(df[FEATURES])
        df["cluster"] = artifacts["kmeans"].predict(X_scaled)
        df["segment"] = df["cluster"].map(artifacts["cluster_to_label"])

    segment_counts = df["segment"].value_counts().to_dict()

    cluster_stats = (
        df.groupby("segment")[FEATURES]
        .mean()
        .round(2)
        .reset_index()
        .to_dict(orient="records")
    )

    return {"segments": segment_counts, "cluster_stats": cluster_stats}


if __name__ == "__main__":
    summary = get_segment_summary()
    print(summary)
