import os
import sys
import json
import warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

warnings.filterwarnings('ignore')

# ── Paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(SCRIPT_DIR, 'dataset.csv')
MODELS_DIR = os.path.join(SCRIPT_DIR, 'models')
MODEL_PATH = os.path.join(MODELS_DIR, 'sleep_quality_model.pkl')
METADATA_PATH = os.path.join(MODELS_DIR, 'model_metadata.json')


def time_to_minutes(time_str):
    """Convert 'HH:MM' string to minutes since midnight."""
    try:
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, AttributeError, IndexError):
        return 0


def load_and_inspect(path):
    """Load the CSV and print inspection summary."""
    if not os.path.exists(path):
        print(f"ERROR: Dataset not found at {path}")
        print("Run  python ml/create_dataset.py  first.")
        sys.exit(1)

    df = pd.read_csv(path, keep_default_na=False, na_values=[''])

    print("=" * 60)
    print("  PHASE 1 - Dataset Inspection")
    print("=" * 60)
    print(f"\n  Shape           : {df.shape}")
    print(f"  Missing values  : {df.isnull().sum().sum()}")
    print(f"  Duplicate rows  : {df.duplicated().sum()}")
    print(f"\n  Columns and dtypes:")
    for col in df.columns:
        print(f"    {col:25s} {str(df[col].dtype):10s}  unique={df[col].nunique()}")
    print(f"\n  Target distribution (sleep_quality):")
    print(f"    {df['sleep_quality'].value_counts().to_dict()}")

    return df


def engineer_features(df):
    """
    Convert time columns to numerical minutes-since-midnight.
    Drop the original string columns.
    """
    df = df.copy()
    df['bedtime_minutes'] = df['bedtime'].apply(time_to_minutes)
    df['wake_time_minutes'] = df['wake_time'].apply(time_to_minutes)
    df.drop(columns=['bedtime', 'wake_time'], inplace=True)
    return df


def build_preprocessor():
    """
    Build a ColumnTransformer that handles:
      - Numerical features  → StandardScaler
      - Ordinal categorical → OrdinalEncoder (caffeine has natural order)
      - Nominal categorical → OneHotEncoder (mood, interruptions)
    """
    numerical_features = [
        'sleep_duration', 'exercise_duration', 'screen_time',
        'stress_level', 'bedtime_minutes', 'wake_time_minutes'
    ]
    ordinal_features = ['caffeine']
    nominal_features = ['mood', 'interruptions']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('ord', OrdinalEncoder(
                categories=[['None', 'Low', 'Moderate', 'High']]
            ), ordinal_features),
            ('nom', OneHotEncoder(
                drop='first', sparse_output=False, handle_unknown='infrequent_if_exist'
            ), nominal_features),
        ],
        remainder='drop'
    )
    return preprocessor


def train_and_evaluate(X_train, X_test, y_train, y_test, preprocessor):
    """
    Train 4 models, evaluate each, print comparison table,
    and return the best pipeline.
    """
    models = {
        'Logistic Regression': LogisticRegression(
            max_iter=1000, random_state=42
        ),
        'Decision Tree': DecisionTreeClassifier(
            random_state=42, max_depth=10
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=100, random_state=42, max_depth=15
        ),
        'SVM': SVC(
            kernel='rbf', random_state=42, probability=True
        ),
    }

    results = {}
    best_f1 = -1
    best_name = None
    best_pipeline = None

    print("\n" + "=" * 60)
    print("  PHASE 2 - Model Training & Evaluation")
    print("=" * 60)

    for name, model in models.items():
        # Build full pipeline: preprocessor → model
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])

        # Train
        pipeline.fit(X_train, y_train)

        # Predict
        y_pred = pipeline.predict(X_test)

        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        results[name] = {
            'accuracy': round(acc, 4),
            'precision': round(prec, 4),
            'recall': round(rec, 4),
            'f1': round(f1, 4),
        }

        if f1 > best_f1:
            best_f1 = f1
            best_name = name
            best_pipeline = pipeline

        print(f"\n  -- {name} --")
        print(f"    Accuracy  : {acc:.4f}")
        print(f"    Precision : {prec:.4f}")
        print(f"    Recall    : {rec:.4f}")
        print(f"    F1 Score  : {f1:.4f}")
        print(f"    Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred, labels=['Good', 'Average', 'Poor'])
        for row_label, row in zip(['Good', 'Average', 'Poor'], cm):
            print(f"      {row_label:8s} {row}")

    # -- Comparison Table --
    print("\n" + "=" * 60)
    print("  MODEL COMPARISON TABLE")
    print("=" * 60)
    print(f"\n  {'Model':<22s} {'Accuracy':>9s} {'Precision':>10s} {'Recall':>8s} {'F1':>8s}")
    print(f"  {'-'*22} {'-'*9} {'-'*10} {'-'*8} {'-'*8}")
    for name, metrics in results.items():
        marker = " [BEST]" if name == best_name else ""
        print(f"  {name:<22s} {metrics['accuracy']:>9.4f} {metrics['precision']:>10.4f} "
              f"{metrics['recall']:>8.4f} {metrics['f1']:>8.4f}{marker}")

    print(f"\n  >> Best model: {best_name} (F1 = {best_f1:.4f})")

    return best_pipeline, best_name, results


def save_model(pipeline, model_name, results, labels):
    """Save the trained pipeline and metadata."""
    os.makedirs(MODELS_DIR, exist_ok=True)

    # Save pipeline (preprocessor + model)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"\n  [OK] Model pipeline saved to: {MODEL_PATH}")

    # Save metadata
    metadata = {
        'selected_model': model_name,
        'labels': labels,
        'feature_columns': [
            'sleep_duration', 'bedtime_minutes', 'wake_time_minutes',
            'caffeine', 'exercise_duration', 'screen_time',
            'stress_level', 'mood', 'interruptions'
        ],
        'comparison_results': results,
    }
    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  [OK] Metadata saved to: {METADATA_PATH}")


def main():
    # ── Load & inspect ──
    df = load_and_inspect(DATASET_PATH)

    # ── Clean ──
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    print(f"\n  After cleaning: {df.shape[0]} rows")

    # ── Feature engineering ──
    df = engineer_features(df)

    # ── Separate features / target ──
    TARGET = 'sleep_quality'
    X = df.drop(columns=[TARGET])
    y = df[TARGET]
    labels = sorted(y.unique().tolist())

    print(f"\n  Features: {list(X.columns)}")
    print(f"  Labels  : {labels}")

    # ── Train/test split (stratified, no data leakage) ──
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n  Train set: {X_train.shape[0]} samples")
    print(f"  Test set : {X_test.shape[0]} samples")

    # ── Build preprocessor ──
    preprocessor = build_preprocessor()

    # ── Train, evaluate, select best ──
    best_pipeline, best_name, results = train_and_evaluate(
        X_train, X_test, y_train, y_test, preprocessor
    )

    # ── Save ──
    save_model(best_pipeline, best_name, results, labels)

    # ── Final classification report ──
    y_pred = best_pipeline.predict(X_test)
    print(f"\n  -- Final Classification Report ({best_name}) --")
    print(classification_report(y_test, y_pred, target_names=['Average', 'Good', 'Poor']))

    print("\n" + "=" * 60)
    print("  Training complete! Model is ready for predictions.")
    print("=" * 60)


if __name__ == '__main__':
    main()
