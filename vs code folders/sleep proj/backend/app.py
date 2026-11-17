import os
import sys
import json
import traceback
import joblib
from flask import Flask, request, jsonify, send_from_directory

# Add project root to path so we can import sibling modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from preprocessing import validate_input, preprocess_input
from recommendations import generate_recommendations

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'models', 'sleep_quality_model.pkl')
METADATA_PATH = os.path.join(BASE_DIR, 'ml', 'models', 'model_metadata.json')

# ── Flask App ──────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=FRONTEND_DIR)

# ── Load model at startup ──────────────────────────────────────────────
model_pipeline = None
model_metadata = None


def load_model():
    """Load the trained model pipeline and metadata."""
    global model_pipeline, model_metadata

    if not os.path.exists(MODEL_PATH):
        print(f"[WARNING] Model not found at {MODEL_PATH}")
        print("  Run  python ml/train_model.py  first.")
        return False

    try:
        model_pipeline = joblib.load(MODEL_PATH)
        print(f"[OK] Model loaded from {MODEL_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return False

    if os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, 'r') as f:
                model_metadata = json.load(f)
            print(f"[OK] Metadata loaded: {model_metadata.get('selected_model', 'unknown')}")
        except Exception as e:
            print(f"[WARNING] Could not load metadata: {e}")

    return True


# ── Routes ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve the frontend index.html."""
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    """Serve static frontend files (CSS, JS, images)."""
    return send_from_directory(FRONTEND_DIR, filename)


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict sleep quality from user input.

    Expects JSON body:
    {
        "sleep_duration": 7.5,
        "bedtime": "23:00",
        "wake_time": "06:30",
        "caffeine": "Moderate",
        "exercise": 30,
        "screen_time": 60,
        "stress": 6,
        "mood": "Neutral",
        "interruptions": "No"
    }

    Returns JSON:
    {
        "prediction": "Good",
        "confidence": 0.87,
        "tips": ["...", "..."]
    }
    """
    # ── Check model is loaded ──
    if model_pipeline is None:
        return jsonify({
            'error': 'Model not loaded. Please train the model first.',
            'details': 'Run: python ml/train_model.py'
        }), 503

    # ── Parse JSON ──
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({
            'error': 'Invalid JSON in request body.'
        }), 400

    if not data:
        return jsonify({
            'error': 'Empty request body. Please provide sleep data.'
        }), 400

    # ── Validate input ──
    is_valid, errors = validate_input(data)
    if not is_valid:
        return jsonify({
            'error': 'Validation failed.',
            'details': errors
        }), 400

    # ── Preprocess ──
    try:
        input_df = preprocess_input(data)
    except Exception as e:
        print(f"[ERROR] Preprocessing failed: {traceback.format_exc()}")
        return jsonify({
            'error': 'Failed to preprocess input data.'
        }), 500

    # ── Predict ──
    try:
        prediction = model_pipeline.predict(input_df)[0]

        # Get confidence (probability) if the model supports it
        confidence = None
        if hasattr(model_pipeline, 'predict_proba'):
            try:
                proba = model_pipeline.predict_proba(input_df)[0]
                confidence = round(float(max(proba)), 4)
            except Exception:
                # Some models may not support predict_proba reliably
                confidence = None

    except Exception as e:
        print(f"[ERROR] Prediction failed: {traceback.format_exc()}")
        return jsonify({
            'error': 'Prediction failed. The model may be corrupted.'
        }), 500

    # ── Generate recommendations ──
    try:
        tips = generate_recommendations(data, prediction)
    except Exception as e:
        print(f"[WARNING] Recommendation generation failed: {e}")
        tips = ["Maintain a consistent sleep schedule for better rest."]

    # ── Build response ──
    response = {
        'prediction': prediction,
        'tips': tips
    }
    if confidence is not None:
        response['confidence'] = confidence

    return jsonify(response), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'model_loaded': model_pipeline is not None,
        'model_name': model_metadata.get('selected_model') if model_metadata else None
    }), 200


# ── Error Handlers ─────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found.'}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed.'}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error.'}), 500


# ── Main ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("  SLEEP QUALITY PREDICTOR - Flask Server")
    print("=" * 60)

    loaded = load_model()
    if not loaded:
        print("\n[WARNING] Server starting WITHOUT a trained model.")
        print("  The /predict endpoint will return 503 until a model is loaded.")

    print(f"\n  Frontend served from: {FRONTEND_DIR}")
    print(f"  Computer: http://127.0.0.1:5000")
    print(f"  Same Wi-Fi devices: http://<your-computer-ip>:5000")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
