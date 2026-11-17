"""
Preprocessing Module — Sleep Quality Predictor

Converts raw user input (from the /predict API) into the feature format
expected by the trained scikit-learn pipeline.

The pipeline itself handles scaling and encoding — this module only
converts JSON fields into the correct DataFrame structure.
"""

import pandas as pd


def time_to_minutes(time_str):
    """
    Convert a time string 'HH:MM' to minutes since midnight.

    Examples:
        '23:00' → 1380
        '06:30' → 390
        '00:15' → 15

    Returns 0 if parsing fails.
    """
    try:
        parts = time_str.strip().split(':')
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        return hours * 60 + minutes
    except (ValueError, AttributeError, IndexError):
        return 0


def validate_input(data):
    """
    Validate raw input data from the API request.

    Args:
        data (dict): Raw JSON from the request body.

    Returns:
        tuple: (is_valid: bool, errors: list[str])
    """
    errors = []

    # Required fields
    required = [
        'sleep_duration', 'bedtime', 'wake_time', 'caffeine',
        'exercise', 'screen_time', 'stress', 'mood', 'interruptions'
    ]
    for field in required:
        if field not in data or data[field] is None or str(data[field]).strip() == '':
            errors.append(f"'{field}' is required.")

    if errors:
        return False, errors

    # Sleep duration: positive number
    try:
        sd = float(data['sleep_duration'])
        if sd <= 0 or sd > 24:
            errors.append("Sleep duration must be between 0.1 and 24 hours.")
    except (ValueError, TypeError):
        errors.append("Sleep duration must be a valid number.")

    # Exercise: non-negative number
    try:
        ex = float(data['exercise'])
        if ex < 0 or ex > 300:
            errors.append("Exercise duration must be between 0 and 300 minutes.")
    except (ValueError, TypeError):
        errors.append("Exercise duration must be a valid number.")

    # Screen time: non-negative number
    try:
        st = float(data['screen_time'])
        if st < 0 or st > 600:
            errors.append("Screen time must be between 0 and 600 minutes.")
    except (ValueError, TypeError):
        errors.append("Screen time must be a valid number.")

    # Stress: 0–10
    try:
        stress = float(data['stress'])
        if stress < 0 or stress > 10:
            errors.append("Stress level must be between 0 and 10.")
    except (ValueError, TypeError):
        errors.append("Stress level must be a valid number.")

    # Caffeine: valid option
    valid_caffeine = ['None', 'Low', 'Moderate', 'High']
    if data.get('caffeine') not in valid_caffeine:
        errors.append(f"Caffeine must be one of: {', '.join(valid_caffeine)}.")

    # Mood: valid option
    valid_moods = ['Happy', 'Neutral', 'Sad', 'Anxious']
    if data.get('mood') not in valid_moods:
        errors.append(f"Mood must be one of: {', '.join(valid_moods)}.")

    # Interruptions: valid option
    valid_interruptions = ['Yes', 'No']
    if data.get('interruptions') not in valid_interruptions:
        errors.append(f"Interruptions must be one of: {', '.join(valid_interruptions)}.")

    # Time fields: basic format check
    for time_field in ['bedtime', 'wake_time']:
        val = str(data.get(time_field, ''))
        if ':' not in val:
            errors.append(f"'{time_field}' must be in HH:MM format.")

    return len(errors) == 0, errors


def preprocess_input(data):
    """
    Convert validated user input into a single-row DataFrame
    matching the feature columns expected by the trained pipeline.

    The scikit-learn Pipeline handles scaling and encoding internally;
    this function only structures the data correctly.

    Args:
        data (dict): Validated user input.

    Returns:
        pd.DataFrame: Single-row DataFrame with the correct columns.
    """
    row = {
        'sleep_duration': float(data['sleep_duration']),
        'caffeine': data['caffeine'],
        'exercise_duration': float(data['exercise']),
        'screen_time': float(data['screen_time']),
        'stress_level': float(data['stress']),
        'mood': data['mood'],
        'interruptions': data['interruptions'],
        'bedtime_minutes': time_to_minutes(data['bedtime']),
        'wake_time_minutes': time_to_minutes(data['wake_time']),
    }

    # Create DataFrame with exact column order matching training
    df = pd.DataFrame([row])
    return df
