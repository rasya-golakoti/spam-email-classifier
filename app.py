# app.py - UPDATED TO USE YOUR EXISTING TF-IDF MODELS
from flask import Flask, render_template, request, jsonify
import pickle
import re
import os
import joblib

app = Flask(__name__)

# Global variables for model and vectorizer
model = None
vectorizer = None
model_loaded = False

# Clean email function (same as training)
def clean_email(text):
    """Clean email text - MUST MATCH THE TRAINING PREPROCESSOR"""
    try:
        # Split to remove headers (after first \n\n)
        parts = text.split('\n\n', 1)
        if len(parts) > 1:
            text = parts[1]
        else:
            text = parts[0]
            
        text = text.lower()
        text = re.sub(r'http\S+', 'URL', text)
        text = re.sub(r'\d+', 'NUMBER', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text
    except Exception as e:
        print(f"Warning in clean_email: {e}")
        return text.lower() if text else ""

def load_model():
    """Load the trained model and vectorizer"""
    global model, vectorizer, model_loaded
    
    try:
        print("🔍 Checking for model files...")
        
        # Check if model files exist - try different formats
        model_files = [
            ('spam_model.joblib', 'joblib'),
            ('spam_model.pkl', 'pickle'),
            ('best_spam_model.pkl', 'pickle')
        ]
        
        vectorizer_files = [
            ('tfidf_vectorizer.joblib', 'joblib'),
            ('tfidf_vectorizer.pkl', 'pickle'),
            ('count_vectorizer.pkl', 'pickle')
        ]
        
        # Try to load vectorizer
        vectorizer_loaded = False
        for filename, loader_type in vectorizer_files:
            filepath = os.path.join('models', filename)
            if os.path.exists(filepath):
                print(f"📦 Loading vectorizer from: {filename}")
                try:
                    if loader_type == 'joblib':
                        vectorizer = joblib.load(filepath)
                    else:  # pickle
                        with open(filepath, 'rb') as f:
                            vectorizer = pickle.load(f)
                    print(f"✅ Vectorizer loaded from {filename}")
                    vectorizer_loaded = True
                    break
                except Exception as e:
                    print(f"⚠️ Failed to load {filename}: {e}")
                    continue
        
        if not vectorizer_loaded:
            print("❌ Could not load any vectorizer file!")
            return False
        
        # Try to load model
        model_loaded_flag = False
        for filename, loader_type in model_files:
            filepath = os.path.join('models', filename)
            if os.path.exists(filepath):
                print(f"🤖 Loading model from: {filename}")
                try:
                    if loader_type == 'joblib':
                        model = joblib.load(filepath)
                    else:  # pickle
                        with open(filepath, 'rb') as f:
                            model = pickle.load(f)
                    print(f"✅ Model loaded from {filename}")
                    model_loaded_flag = True
                    break
                except Exception as e:
                    print(f"⚠️ Failed to load {filename}: {e}")
                    continue
        
        if not model_loaded_flag:
            print("❌ Could not load any model file!")
            return False
        
        # Test the loaded model with a simple prediction
        print("🧪 Testing loaded model...")
        try:
            test_text = "This is a test email"
            cleaned = clean_email(test_text)
            test_vec = vectorizer.transform([cleaned])
            prediction = model.predict(test_vec)
            print(f"✅ Model test successful! Prediction shape: {prediction.shape}")
            
            model_loaded = True
            return True
        except Exception as e:
            print(f"❌ Model test failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

# Load model when the app starts
print("🚀 Initializing Flask application...")
print(f"📁 Working directory: {os.getcwd()}")
print(f"📁 Models directory exists: {os.path.exists('models')}")
if os.path.exists('models'):
    print(f"📁 Files in models directory: {os.listdir('models')}")

load_model()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not model_loaded:
        return jsonify({
            'error': 'Model not loaded. Please run create_model.py first.',
            'prediction': 'ERROR',
            'confidence': 0,
            'ham_probability': 0,
            'spam_probability': 0,
            'is_spam': False
        })
    
    try:
        # Get email text from form
        email_text = request.form.get('email', '')
        
        if not email_text.strip():
            return jsonify({
                'error': 'Please enter email text',
                'prediction': 'INVALID',
                'confidence': 0,
                'ham_probability': 0,
                'spam_probability': 0,
                'is_spam': False
            })
        
        # Clean the email
        cleaned_email = clean_email(email_text)
        
        print(f"📧 Processing email (cleaned length: {len(cleaned_email)})")
        print(f"📧 First 200 chars of cleaned email: {cleaned_email[:200]}")
        
        # Vectorize
        email_vec = vectorizer.transform([cleaned_email])
        print(f"📊 Vector shape: {email_vec.shape}")
        
        # Make prediction
        prediction = model.predict(email_vec)[0]
        print(f"📊 Raw prediction: {prediction}")
        
        # Get probabilities (check if model has predict_proba)
        if hasattr(model, 'predict_proba'):
            prediction_proba = model.predict_proba(email_vec)[0]
            print(f"📊 Probabilities: {prediction_proba}")
        else:
            # For models without predict_proba, use decision function or default
            print("⚠️ Model doesn't have predict_proba method")
            if hasattr(model, 'decision_function'):
                decision = model.decision_function(email_vec)[0]
                # Convert to probability-like scores
                ham_prob = max(0, min(100, 100 - (decision * 10)))
                spam_prob = 100 - ham_prob
                prediction_proba = [ham_prob/100, spam_prob/100]
            else:
                # Default probabilities
                prediction_proba = [0.5, 0.5] if prediction == 1 else [0.5, 0.5]
        
        # Get probabilities
        ham_prob = prediction_proba[0] * 100
        spam_prob = prediction_proba[1] * 100
        
        # Prepare response
        result = {
            'prediction': 'SPAM' if prediction == 1 else 'HAM',
            'ham_probability': round(ham_prob, 2),
            'spam_probability': round(spam_prob, 2),
            'confidence': round(max(ham_prob, spam_prob), 2),
            'is_spam': bool(prediction == 1),
            'error': None
        }
        
        print(f"📊 Prediction result: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': f'Prediction error: {str(e)}',
            'prediction': 'ERROR',
            'confidence': 0,
            'ham_probability': 0,
            'spam_probability': 0,
            'is_spam': False
        })

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for programmatic access"""
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'JSON with "email" field is required'}), 400
        
        email_text = data.get('email', '')
        
        if not email_text.strip():
            return jsonify({'error': 'Email text is required'}), 400
        
        # Clean and predict
        cleaned_email = clean_email(email_text)
        email_vec = vectorizer.transform([cleaned_email])
        prediction = model.predict(email_vec)[0]
        
        # Get probabilities
        if hasattr(model, 'predict_proba'):
            prediction_proba = model.predict_proba(email_vec)[0]
        else:
            prediction_proba = [0.5, 0.5] if prediction == 1 else [0.5, 0.5]
        
        return jsonify({
            'prediction': 'spam' if prediction == 1 else 'ham',
            'probabilities': {
                'ham': float(prediction_proba[0]),
                'spam': float(prediction_proba[1])
            },
            'is_spam': bool(prediction == 1),
            'confidence': float(max(prediction_proba))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok' if model_loaded else 'error',
        'model_loaded': model_loaded,
        'vectorizer_type': type(vectorizer).__name__ if model_loaded else None,
        'model_type': type(model).__name__ if model_loaded else None,
        'service': 'spam-detector',
        'message': 'Model loaded and ready' if model_loaded else 'Model not loaded. Run create_model.py first.'
    })

@app.route('/test')
def test_endpoint():
    """Test endpoint to verify the app is running"""
    return jsonify({
        'message': 'Flask app is running!',
        'model_loaded': model_loaded,
        'endpoints': {
            'home': '/',
            'predict': '/predict (POST)',
            'api_predict': '/api/predict (POST)',
            'health': '/health',
            'test': '/test'
        }
    })

@app.route('/model_info')
def model_info():
    """Get model information"""
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    info = {
        'vectorizer': {
            'type': type(vectorizer).__name__,
            'features': vectorizer.get_feature_names_out().shape[0] if hasattr(vectorizer, 'get_feature_names_out') else 'Unknown',
            'max_features': vectorizer.max_features if hasattr(vectorizer, 'max_features') else 'Unknown'
        },
        'model': {
            'type': type(model).__name__,
            'has_predict_proba': hasattr(model, 'predict_proba'),
            'has_decision_function': hasattr(model, 'decision_function')
        }
    }
    
    return jsonify(info)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌐 Spam Email Detector Web Application")
    print("="*50)
    
    if model_loaded:
        print("✅ Model is loaded and ready!")
        print(f"   - Vectorizer type: {type(vectorizer).__name__}")
        print(f"   - Model type: {type(model).__name__}")
        
        # Try to get feature count
        try:
            if hasattr(vectorizer, 'get_feature_names_out'):
                features = vectorizer.get_feature_names_out()
                print(f"   - Features: {len(features)}")
        except:
            pass
    else:
        print("⚠️  WARNING: Model not loaded!")
        print("   Please check:")
        print("   1. Run 'python create_model.py' to train and save the model")
        print("   2. Check that 'models/' directory exists with model files")
        print("   3. The web interface will work, but predictions will fail.")
    
    print("\n📡 Available endpoints:")
    print("   - Web interface: http://localhost:5000")
    print("   - Health check: http://localhost:5000/health")
    print("   - Model info: http://localhost:5000/model_info")
    print("   - Test endpoint: http://localhost:5000/test")
    print("   - API: POST http://localhost:5000/api/predict")
    print("\n🔧 Starting Flask server...")
    print("="*50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to avoid model loading issues
    )