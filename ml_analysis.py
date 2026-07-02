"""
Machine learning analysis for POW-Consensus.

Uses Random Forest to predict the best mining node without data leakage.
Features used:
Temp, Humidity, Tx, Difficulty, MEGA_Response_ms, ESP32_Response_ms
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


DATASET_PATH = Path("final_dataset.csv")
MODEL_PATH = Path("pow_consensus_random_forest.joblib")

FEATURES = [
    "Temp",
    "Humidity",
    "Tx",
    "Difficulty",
    "MEGA_Response_ms",
    "ESP32_Response_ms",
]
TARGET = "Winner"


def load_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path.resolve()}")

    df = pd.read_csv(path)
    required_columns = FEATURES + [TARGET]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    df = df.dropna(subset=required_columns).copy()
    for column in FEATURES:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=FEATURES + [TARGET]).copy()

    if len(df) < 10:
      raise ValueError("Dataset must contain at least 10 valid rows for ML analysis.")

    return df
    


def train_random_forest(df: pd.DataFrame):
    x = df[FEATURES]
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df[TARGET].astype(str).str.upper())

    stratify = y if len(np.unique(y)) > 1 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.20,
        random_state=42,
        stratify=stratify,
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    probabilities = model.predict_proba(x_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, average="weighted", zero_division=0),
        "recall": recall_score(y_test, predictions, average="weighted", zero_division=0),
        "f1": f1_score(y_test, predictions, average="weighted", zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, predictions),
        "classes": label_encoder.classes_,
        "feature_importance": pd.DataFrame(
            {
                "Feature": FEATURES,
                "Importance": model.feature_importances_,
            }
        ).sort_values("Importance", ascending=False),
        "sample_prediction": label_encoder.inverse_transform([predictions[-1]])[0],
        "sample_confidence": float(np.max(probabilities[-1])),
    }

    return model, label_encoder, metrics


def predict_latest_row(model, label_encoder, df: pd.DataFrame) -> tuple[str, float]:
    latest_features = df[FEATURES].tail(1)
    prediction = model.predict(latest_features)[0]
    probabilities = model.predict_proba(latest_features)[0]
    predicted_label = label_encoder.inverse_transform([prediction])[0]
    confidence = float(np.max(probabilities))
    return predicted_label, confidence


def print_report(metrics: dict, latest_prediction: str, latest_confidence: float) -> None:
    print("\n========== POW-Consensus Random Forest ML Report ==========")
    print(f"Accuracy : {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall   : {metrics['recall']:.4f}")
    print(f"F1 Score : {metrics['f1']:.4f}")

    print("\nClasses:")
    print(", ".join(metrics["classes"]))

    print("\nConfusion Matrix:")
    print(metrics["confusion_matrix"])

    print("\nFeature Importance:")
    print(metrics["feature_importance"].to_string(index=False))

    print("\nPrediction for Latest Dataset Row:")
    print(f"Prediction : {latest_prediction}")
    print(f"Confidence : {latest_confidence:.4f}")
    print("==========================================================\n")


def main() -> None:
    df = load_dataset()
    model, label_encoder, metrics = train_random_forest(df)
    latest_prediction, latest_confidence = predict_latest_row(model, label_encoder, df)

    print_report(metrics, latest_prediction, latest_confidence)

    joblib.dump(
        {
            "model": model,
            "label_encoder": label_encoder,
            "features": FEATURES,
            "metrics": {
                key: value
                for key, value in metrics.items()
                if key not in {"confusion_matrix", "feature_importance"}
            },
        },
        MODEL_PATH,
    )
    print(f"[OK] Model saved to {MODEL_PATH.resolve()}")


if __name__ == "__main__":
    main()