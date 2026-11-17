"""
Model Evaluation Script — Sleep Quality Predictor

Loads the saved model pipeline and evaluates it on the test split.
Generates confusion matrix plot and classification report.

Usage:
  python ml/evaluate_model.py
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score
)

# ── Paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(SCRIPT_DIR, 'dataset.csv')
MODEL_PATH = os.path.join(SCRIPT_DIR, 'models', 'sleep_quality_model.pkl')
METADATA_PATH = os.path.join(SCRIPT_DIR, 'models', 'model_metadata.json')
PLOTS_DIR = os.path.join(SCRIPT_DIR, 'models', 'plots')


def time_to_minutes(time_str):
    """Convert 'HH:MM' to minutes since midnight."""
    try:
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, AttributeError, IndexError):
        return 0


def main():
    # ── Check files ──
    for path, label in [(DATASET_PATH, 'Dataset'), (MODEL_PATH, 'Model')]:
        if not os.path.exists(path):
            print(f"ERROR: {label} not found at {path}")
            sys.exit(1)

    # ── Load ──
    df = pd.read_csv(DATASET_PATH, keep_default_na=False, na_values=[''])
    pipeline = joblib.load(MODEL_PATH)

    with open(METADATA_PATH, 'r') as f:
        metadata = json.load(f)

    print("=" * 60)
    print("  SLEEP QUALITY PREDICTOR — Model Evaluation")
    print("=" * 60)
    print(f"\n  Model: {metadata['selected_model']}")

    # ── Feature engineering (same as training) ──
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    df['bedtime_minutes'] = df['bedtime'].apply(time_to_minutes)
    df['wake_time_minutes'] = df['wake_time'].apply(time_to_minutes)
    df.drop(columns=['bedtime', 'wake_time'], inplace=True)

    TARGET = 'sleep_quality'
    X = df.drop(columns=[TARGET])
    y = df[TARGET]

    # ── Same split as training ──
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── Predict ──
    y_pred = pipeline.predict(X_test)
    labels = ['Good', 'Average', 'Poor']

    # ── Metrics ──
    acc = accuracy_score(y_test, y_pred)
    print(f"\n  Overall Accuracy: {acc:.4f}")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=labels))

    # ── Confusion Matrix Plot ──
    os.makedirs(PLOTS_DIR, exist_ok=True)
    cm = confusion_matrix(y_test, y_pred, labels=labels)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues',
        xticklabels=labels, yticklabels=labels,
        linewidths=0.5, ax=ax
    )
    ax.set_xlabel('Predicted', fontsize=12)
    ax.set_ylabel('Actual', fontsize=12)
    ax.set_title(f'Confusion Matrix — {metadata["selected_model"]}', fontsize=14)
    plt.tight_layout()

    plot_path = os.path.join(PLOTS_DIR, 'confusion_matrix.png')
    fig.savefig(plot_path, dpi=150)
    print(f"\n  [OK] Confusion matrix saved to: {plot_path}")

    # ── Model comparison bar chart ──
    if 'comparison_results' in metadata:
        results = metadata['comparison_results']
        model_names = list(results.keys())
        metrics_names = ['accuracy', 'precision', 'recall', 'f1']

        fig2, ax2 = plt.subplots(figsize=(10, 6))
        x = np.arange(len(model_names))
        width = 0.2

        for i, metric in enumerate(metrics_names):
            values = [results[m][metric] for m in model_names]
            ax2.bar(x + i * width, values, width, label=metric.capitalize())

        ax2.set_xlabel('Model', fontsize=12)
        ax2.set_ylabel('Score', fontsize=12)
        ax2.set_title('Model Comparison', fontsize=14)
        ax2.set_xticks(x + width * 1.5)
        ax2.set_xticklabels(model_names, rotation=15, ha='right')
        ax2.legend()
        ax2.set_ylim(0, 1.1)
        plt.tight_layout()

        comparison_path = os.path.join(PLOTS_DIR, 'model_comparison.png')
        fig2.savefig(comparison_path, dpi=150)
        print(f"  [OK] Model comparison chart saved to: {comparison_path}")

    print("\n" + "=" * 60)
    print("  Evaluation complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
