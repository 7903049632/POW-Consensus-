"""
Graph analysis for POW-Consensus final_dataset.csv.

Generates:
1. Winner Distribution
2. Response Time Comparison
3. Temperature Distribution
4. Humidity Distribution
5. Transaction Count Distribution
6. Difficulty Distribution
7. Correlation Heatmap
8. Feature Importance
9. Confusion Matrix
10. Accuracy Chart
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


DATASET_PATH = Path("final_dataset.csv")
GRAPH_DIR = Path("graphs")

FEATURES = [
    "Temp",
    "Humidity",
    "Tx",
    "Difficulty",
    "MEGA_Response_ms",
    "ESP32_Response_ms",
]

TARGET = "Winner"

sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.family"] = "DejaVu Sans"


def load_dataset() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH.resolve()}")

    df = pd.read_csv(DATASET_PATH)

    required_columns = [
        "Epoch",
        "Temp",
        "Humidity",
        "Tx",
        "Difficulty",
        "MEGA_Response_ms",
        "ESP32_Response_ms",
        "MEGA_Score",
        "ESP32_Score",
        "Winner",
        "Validation",
    ]

    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    numeric_columns = [
        "Epoch",
        "Temp",
        "Humidity",
        "Tx",
        "Difficulty",
        "MEGA_Response_ms",
        "ESP32_Response_ms",
        "MEGA_Score",
        "ESP32_Score",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=numeric_columns + ["Winner", "Validation"]).copy()

    if df.empty:
        raise ValueError("Dataset has no valid rows after cleaning.")

    return df


def save_current_figure(filename: str) -> None:
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GRAPH_DIR / filename

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    print(f"[OK] Saved {output_path.resolve()}")


def winner_distribution(df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 6))

    ax = sns.countplot(
        data=df,
        x="Winner",
        hue="Winner",
        palette="Set2",
        legend=False,
    )

    ax.set_title("Winner Distribution")
    ax.set_xlabel("Mining Node")
    ax.set_ylabel("Number of Wins")

    for container in ax.containers:
        ax.bar_label(container, fmt="%d")

    save_current_figure("winner_distribution.png")


def response_time_comparison(df: pd.DataFrame) -> None:
    response_df = df[["MEGA_Response_ms", "ESP32_Response_ms"]].melt(
        var_name="Node",
        value_name="Response Time (ms)",
    )

    response_df["Node"] = response_df["Node"].str.replace(
        "_Response_ms",
        "",
        regex=False,
    )

    plt.figure(figsize=(10, 6))

    ax = sns.boxplot(
        data=response_df,
        x="Node",
        y="Response Time (ms)",
        hue="Node",
        palette="Set3",
        legend=False,
    )

    sns.stripplot(
        data=response_df,
        x="Node",
        y="Response Time (ms)",
        color="black",
        alpha=0.20,
        size=2,
    )

    ax.set_title("Response Time Comparison")
    ax.set_xlabel("Mining Node")

    save_current_figure("response_time_comparison.png")


def distribution_plot(
    df: pd.DataFrame,
    column: str,
    title: str,
    filename: str,
    color: str,
) -> None:
    plt.figure(figsize=(10, 6))

    ax = sns.histplot(
        df[column],
        kde=True,
        bins=25,
        color=color,
    )

    ax.set_title(title)
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")

    save_current_figure(filename)


def correlation_heatmap(df: pd.DataFrame) -> None:
    columns = [
        "Temp",
        "Humidity",
        "Tx",
        "Difficulty",
        "MEGA_Response_ms",
        "ESP32_Response_ms",
        "MEGA_Score",
        "ESP32_Score",
    ]

    plt.figure(figsize=(12, 8))

    ax = sns.heatmap(
        df[columns].corr(),
        annot=True,
        fmt=".2f",
        cmap="vlag",
        center=0,
        linewidths=0.5,
        cbar_kws={"label": "Correlation"},
    )

    ax.set_title("Correlation Heatmap")

    save_current_figure("correlation_heatmap.png")


def train_model_for_graphs(df: pd.DataFrame):
    label_encoder = LabelEncoder()

    x = df[FEATURES]
    y = label_encoder.fit_transform(df[TARGET].astype(str).str.upper())

    stratify = y if len(set(y)) > 1 else None

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.20,
        random_state=42,
        stratify=stratify,
    )

    model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    matrix = confusion_matrix(y_test, predictions)

    return model, label_encoder, accuracy, matrix


def feature_importance_graph(model) -> None:
    importance_df = pd.DataFrame(
        {
            "Feature": FEATURES,
            "Importance": model.feature_importances_,
        }
    ).sort_values("Importance", ascending=True)

    plt.figure(figsize=(10, 6))

    ax = sns.barplot(
        data=importance_df,
        x="Importance",
        y="Feature",
        hue="Feature",
        palette="viridis",
        legend=False,
    )

    ax.set_title("Random Forest Feature Importance")
    ax.set_xlabel("Importance")
    ax.set_ylabel("Feature")

    save_current_figure("feature_importance.png")


def confusion_matrix_graph(matrix, labels) -> None:
    plt.figure(figsize=(8, 6))

    ax = sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        cbar=False,
    )

    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted Winner")
    ax.set_ylabel("Actual Winner")

    save_current_figure("confusion_matrix.png")


def accuracy_chart(accuracy: float) -> None:
    plt.figure(figsize=(8, 6))

    ax = sns.barplot(
        x=["Random Forest"],
        y=[accuracy],
        color="#4C78A8",
    )

    ax.set_ylim(0, 1)
    ax.set_title("Model Accuracy")
    ax.set_xlabel("Model")
    ax.set_ylabel("Accuracy")
    ax.bar_label(ax.containers[0], labels=[f"{accuracy:.2%}"])

    save_current_figure("accuracy_chart.png")


def main() -> None:
    df = load_dataset()

    winner_distribution(df)
    response_time_comparison(df)

    distribution_plot(
        df,
        "Temp",
        "Temperature Distribution",
        "temperature_distribution.png",
        "#E45756",
    )

    distribution_plot(
        df,
        "Humidity",
        "Humidity Distribution",
        "humidity_distribution.png",
        "#72B7B2",
    )

    distribution_plot(
        df,
        "Tx",
        "Transaction Count Distribution",
        "transaction_count_distribution.png",
        "#F58518",
    )

    distribution_plot(
        df,
        "Difficulty",
        "Difficulty Distribution",
        "difficulty_distribution.png",
        "#54A24B",
    )

    correlation_heatmap(df)

    model, label_encoder, accuracy, matrix = train_model_for_graphs(df)

    feature_importance_graph(model)
    confusion_matrix_graph(matrix, label_encoder.classes_)
    accuracy_chart(accuracy)

    print("[COMPLETE] All POW-Consensus graphs generated as PNG files.")


if __name__ == "__main__":
    main()