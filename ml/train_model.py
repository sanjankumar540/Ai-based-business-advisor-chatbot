"""
ml/train_model.py
------------------
Trains the Business Risk Prediction model (Random Forest) on
data/business_dataset.csv, evaluates it, and saves:
    ml/model.pkl      - the trained RandomForestClassifier
    ml/encoders.pkl   - the LabelEncoders used for categorical columns

Run with:
    python ml/train_model.py

NOTE: data/business_dataset.csv is a SYNTHETIC, academically-generated
dataset created for demonstration purposes only. Metrics printed below
reflect performance on this synthetic data, not real-world business
outcomes, and must not be presented as guaranteed real-world accuracy.
"""

import os
import sys
import pickle

# allow running this script directly (python ml/train_model.py) from repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

from config import Config
from ml.preprocessing import (
    load_dataset, encode_features, FEATURE_COLUMNS, TARGET_COLUMN
)


def main():
    dataset_path = os.path.join(Config.DATA_DIR, "business_dataset.csv")
    print(f"[1/6] Loading dataset from {dataset_path} ...")
    df = load_dataset(dataset_path)
    print(f"      Loaded {len(df)} rows.")
    print("      NOTE: This is a synthetic academic demonstration dataset.")

    print("[2/6] Encoding categorical features ...")
    encoders = {}
    df_encoded, encoders = encode_features(df, encoders, fit=True)

    X = df_encoded[FEATURE_COLUMNS]
    y = df_encoded[TARGET_COLUMN]

    print("[3/6] Splitting train/test data (80/20) ...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("[4/6] Training Random Forest Classifier ...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    print("[5/6] Evaluating model on test set ...")
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print("\n===== MODEL EVALUATION (synthetic demo dataset) =====")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-score : {f1:.4f}")
    print("\nConfusion Matrix (rows=actual, cols=predicted):")
    print(cm)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print("=======================================================\n")

    print("[6/6] Saving trained model and encoders ...")
    os.makedirs(Config.ML_DIR, exist_ok=True)
    with open(Config.MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(Config.ENCODERS_PATH, "wb") as f:
        pickle.dump(encoders, f)

    print(f"      Model saved to   : {Config.MODEL_PATH}")
    print(f"      Encoders saved to: {Config.ENCODERS_PATH}")
    print("\nDone. You can now run predictions via ml/predict.py or the web app.")


if __name__ == "__main__":
    main()
