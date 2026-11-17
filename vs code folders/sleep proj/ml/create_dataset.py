"""
Generate a synthetic Sleep Health and Lifestyle dataset.

This dataset is SYNTHETIC — it is generated programmatically with realistic
correlations between features and the target variable. It is NOT sourced
from a real clinical study.

Why synthetic?
- The Kaggle "Sleep Health and Lifestyle Dataset" only contains 4 of our
  9 required UI input features. It lacks: bedtime, wake_time, caffeine,
  screen_time, mood, and interruptions.
- To provide a complete, consistent training set matching ALL 9 UI inputs,
  we generate this dataset with realistic scoring-based labels.

Dataset columns (10):
  - sleep_duration   : float  (3–11 hours)
  - bedtime          : string (HH:MM, 21:00–01:00)
  - wake_time        : string (HH:MM, derived from bedtime + duration)
  - caffeine         : string (None / Low / Moderate / High)
  - exercise_duration: float  (0–120 minutes)
  - screen_time      : float  (10–180 minutes)
  - stress_level     : float  (0–10)
  - mood             : string (Happy / Neutral / Sad / Anxious)
  - interruptions    : string (Yes / No)
  - sleep_quality    : string (Good / Average / Poor) — TARGET

Target label generation:
  A composite quality_score (0–140 range, clipped to 0–100) is computed
  from weighted contributions of each feature, plus Gaussian noise (σ=3).
  Score >= 70 → Good, 40–69 → Average, < 40 → Poor.
"""

import os
import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Number of samples
N_SAMPLES = 500


def generate_dataset(n_samples=N_SAMPLES):
    """Generate the synthetic sleep dataset."""
    data = []

    for _ in range(n_samples):
        # --- Sleep Duration (3–11 hours, normally distributed around 7) ---
        sleep_duration = np.clip(np.random.normal(7, 1.5), 3, 11)
        sleep_duration = round(sleep_duration, 1)

        # --- Bedtime (random between 21:00 and 01:00) ---
        if np.random.random() > 0.3:
            bedtime_hour = np.random.choice(range(21, 24))
        else:
            bedtime_hour = np.random.choice(range(0, 2))
        bedtime_minute = np.random.choice([0, 15, 30, 45])
        bedtime = f"{bedtime_hour:02d}:{bedtime_minute:02d}"

        # --- Wake Time (derived from bedtime + sleep duration) ---
        bedtime_total_min = bedtime_hour * 60 + bedtime_minute
        wake_total_min = (bedtime_total_min + int(sleep_duration * 60)) % (24 * 60)
        wake_hour = wake_total_min // 60
        wake_minute = wake_total_min % 60
        wake_time = f"{wake_hour:02d}:{wake_minute:02d}"

        # --- Caffeine Intake ---
        caffeine = np.random.choice(
            ['None', 'Low', 'Moderate', 'High'],
            p=[0.15, 0.25, 0.35, 0.25]
        )

        # --- Exercise Duration (0–120 minutes, 20% sedentary) ---
        exercise = 0.0 if np.random.random() < 0.2 else round(np.random.uniform(0, 120), 1)

        # --- Screen Time Before Bed (10–180 minutes) ---
        screen_time = round(np.random.uniform(10, 180), 1)

        # --- Stress Level (0–10, continuous) ---
        stress = round(np.random.uniform(0, 10), 1)

        # --- Mood Before Sleep ---
        mood = np.random.choice(
            ['Happy', 'Neutral', 'Sad', 'Anxious'],
            p=[0.25, 0.45, 0.15, 0.15]
        )

        # --- Sleep Interruptions ---
        interruptions = np.random.choice(['Yes', 'No'], p=[0.35, 0.65])

        # ================================================================
        # TARGET: Sleep Quality (composite score → categorical)
        # ================================================================
        quality_score = 0

        # Sleep duration: optimal 6.5–8.5h
        if 6.5 <= sleep_duration <= 8.5:
            quality_score += 25
        elif 5.5 <= sleep_duration <= 9:
            quality_score += 15
        # else: +0

        # Caffeine: lower is better
        caffeine_scores = {'None': 25, 'Low': 20, 'Moderate': 10, 'High': 0}
        quality_score += caffeine_scores[caffeine]

        # Exercise: moderate is best
        if 30 <= exercise <= 90:
            quality_score += 20
        elif exercise >= 15:
            quality_score += 15
        else:
            quality_score += 5

        # Screen time: lower is better
        if screen_time < 30:
            quality_score += 20
        elif screen_time < 60:
            quality_score += 15
        elif screen_time < 120:
            quality_score += 8
        # else: +0

        # Stress: lower is better
        if stress < 3:
            quality_score += 20
        elif stress < 6:
            quality_score += 12
        elif stress < 8:
            quality_score += 5
        # else: +0

        # Mood: happier is better
        mood_scores = {'Happy': 15, 'Neutral': 10, 'Sad': 3, 'Anxious': 0}
        quality_score += mood_scores[mood]

        # Interruptions: no interruptions is better
        quality_score += 15 if interruptions == 'No' else -10

        # Add Gaussian noise to avoid perfect correlation
        quality_score += np.random.normal(0, 3)
        quality_score = np.clip(quality_score, 0, 100)

        # Map score to category
        if quality_score >= 70:
            sleep_quality = 'Good'
        elif quality_score >= 40:
            sleep_quality = 'Average'
        else:
            sleep_quality = 'Poor'

        data.append({
            'sleep_duration': sleep_duration,
            'bedtime': bedtime,
            'wake_time': wake_time,
            'caffeine': caffeine,
            'exercise_duration': exercise,
            'screen_time': screen_time,
            'stress_level': stress,
            'mood': mood,
            'interruptions': interruptions,
            'sleep_quality': sleep_quality
        })

    return pd.DataFrame(data)


def main():
    """Generate dataset and print summary statistics."""
    print("=" * 60)
    print("  SLEEP QUALITY PREDICTOR — Dataset Generator")
    print("=" * 60)

    df = generate_dataset()

    # Save CSV next to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'dataset.csv')
    df.to_csv(csv_path, index=False)

    print(f"\n[OK] Dataset saved to: {csv_path}")
    print(f"  Samples: {len(df)}")
    print(f"  Features: {df.shape[1] - 1}")
    print(f"  Target: sleep_quality")

    print(f"\n--- First 5 rows ---")
    print(df.head().to_string(index=False))

    print(f"\n--- Dataset Info ---")
    print(df.dtypes.to_string())

    print(f"\n--- Missing Values ---")
    print(df.isnull().sum().to_string())

    print(f"\n--- Duplicate Rows: {df.duplicated().sum()} ---")

    print(f"\n--- Target Distribution ---")
    print(df['sleep_quality'].value_counts().to_string())

    print(f"\n--- Categorical Feature Distributions ---")
    for col in ['caffeine', 'mood', 'interruptions']:
        print(f"\n  {col}:")
        print(f"    {df[col].value_counts().to_string()}")

    print(f"\n--- Numerical Feature Statistics ---")
    num_cols = ['sleep_duration', 'exercise_duration', 'screen_time', 'stress_level']
    print(df[num_cols].describe().round(2).to_string())

    print("\n" + "=" * 60)
    print("  Dataset generation complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
