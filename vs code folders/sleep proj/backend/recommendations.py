"""
Recommendation Engine — Sleep Quality Predictor

Generates personalized general wellness suggestions based on the user's
sleep and lifestyle input data.

IMPORTANT: These are general wellness tips for educational purposes.
They do NOT constitute medical advice, diagnosis, or treatment.
"""


def generate_recommendations(data, prediction):
    """
    Generate personalized wellness tips based on user inputs and prediction.

    Args:
        data (dict): Raw user input from the API request.
        prediction (str): The predicted sleep quality ('Good', 'Average', 'Poor').

    Returns:
        list[str]: A list of 3–6 practical wellness suggestions.
    """
    tips = []

    # ── Sleep Duration ──
    sleep_dur = float(data.get('sleep_duration', 7))
    if sleep_dur < 6:
        tips.append(
            "💤 Try to aim for 7–9 hours of sleep. Short sleep duration "
            "can affect energy, mood, and concentration."
        )
    elif sleep_dur > 9:
        tips.append(
            "⏰ Sleeping more than 9 hours regularly can sometimes indicate "
            "underlying issues. Try maintaining a consistent 7–8 hour schedule."
        )

    # ── Caffeine ──
    caffeine = data.get('caffeine', 'None')
    if caffeine == 'High':
        tips.append(
            "☕ Consider reducing caffeine intake, especially after 2 PM. "
            "High caffeine can delay sleep onset and reduce sleep quality."
        )
    elif caffeine == 'Moderate':
        tips.append(
            "☕ Your caffeine intake is moderate. Try to avoid caffeine "
            "within 6 hours of bedtime for better sleep."
        )

    # ── Exercise ──
    exercise = float(data.get('exercise', 0))
    if exercise < 15:
        tips.append(
            "🏃 Regular physical activity can significantly improve sleep quality. "
            "Even a 20–30 minute walk can help."
        )
    elif exercise > 90:
        tips.append(
            "🏋️ Great exercise routine! Just make sure to finish vigorous "
            "workouts at least 2–3 hours before bedtime."
        )

    # ── Screen Time ──
    screen_time = float(data.get('screen_time', 0))
    if screen_time > 120:
        tips.append(
            "📱 High screen time before bed can suppress melatonin production. "
            "Try to put screens away at least 30 minutes before sleep."
        )
    elif screen_time > 60:
        tips.append(
            "📱 Consider reducing screen exposure before bed. "
            "Blue light filters or night mode can also help."
        )

    # ── Stress ──
    stress = float(data.get('stress', 5))
    if stress >= 8:
        tips.append(
            "🧘 High stress levels can significantly impact sleep. "
            "Try relaxation techniques like deep breathing, meditation, or journaling."
        )
    elif stress >= 5:
        tips.append(
            "🧘 Moderate stress detected. Consider a calming bedtime routine — "
            "light stretching, reading, or listening to soft music."
        )

    # ── Mood ──
    mood = data.get('mood', 'Neutral')
    if mood == 'Anxious':
        tips.append(
            "😌 Feeling anxious before bed is common. Try progressive muscle "
            "relaxation or writing down worries before sleeping."
        )
    elif mood == 'Sad':
        tips.append(
            "🌿 If low mood persists, maintaining social connections and a "
            "regular routine can be supportive. Consider talking to someone you trust."
        )

    # ── Sleep Interruptions ──
    interruptions = data.get('interruptions', 'No')
    if interruptions == 'Yes':
        tips.append(
            "🌙 Sleep interruptions can fragment your rest. Try keeping your "
            "room dark, cool, and quiet. Consider earplugs or a white noise machine."
        )

    # ── Bedtime regularity ──
    bedtime = data.get('bedtime', '23:00')
    try:
        hour = int(bedtime.split(':')[0])
        if hour >= 0 and hour <= 3:
            tips.append(
                "🕐 Going to bed very late can disrupt your circadian rhythm. "
                "Try gradually shifting your bedtime earlier by 15–30 minutes."
            )
    except (ValueError, IndexError):
        pass

    # ── Prediction-specific encouragement ──
    if prediction == 'Good':
        tips.insert(0,
            "🌟 Great news! Your sleep habits look healthy. "
            "Keep maintaining your current routine for consistent rest."
        )
    elif prediction == 'Average':
        tips.insert(0,
            "💡 Your sleep quality could use some improvement. "
            "Small changes in your routine can make a big difference."
        )
    elif prediction == 'Poor':
        tips.insert(0,
            "⚠️ Your sleep quality may be below optimal. "
            "Focus on the suggestions below to gradually improve your rest."
        )

    # Ensure at least 3 tips
    general_tips = [
        "🛏️ Maintain a consistent sleep schedule — go to bed and wake up at the same time daily.",
        "🌡️ Keep your bedroom cool (around 18–20°C / 65–68°F) for optimal sleep.",
        "📖 Develop a relaxing pre-sleep routine to signal your body it's time to rest.",
    ]
    while len(tips) < 3:
        for tip in general_tips:
            if tip not in tips:
                tips.append(tip)
                break
        else:
            break

    # Cap at 6 tips
    return tips[:6]
