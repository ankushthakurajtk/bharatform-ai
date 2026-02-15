"""
🇮🇳 BharatForm AI - Render Deployment Version
Lightweight Flask backend for free hosting
"""

import os
import json
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'bharatform-secret-key')

CORS(app)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["100 per minute"])

memory_storage = {}

INDIAN_LANGUAGES = {
    'hi': 'Hindi', 'bn': 'Bengali', 'ta': 'Tamil', 'te': 'Telugu',
    'mr': 'Marathi', 'gu': 'Gujarati', 'kn': 'Kannada', 'ml': 'Malayalam',
    'pa': 'Punjabi', 'or': 'Odia', 'as': 'Assamese', 'ur': 'Urdu', 'en': 'English'
}

def mock_analyze_url(url, language):
    return {
        'session_id': str(uuid.uuid4()),
        'url': url,
        'forms_detected': 1,
        'forms': [{
            'form_id': 'form_1',
            'action': url,
            'method': 'POST',
            'fields': [
                {'name': 'full_name', 'type': 'text', 'required': True, 'label': 'Full Name'},
                {'name': 'email', 'type': 'email', 'required': True, 'label': 'Email'},
                {'name': 'phone', 'type': 'tel', 'required': True, 'label': 'Phone'},
                {'name': 'address', 'type': 'textarea', 'required': False, 'label': 'Address'},
                {'name': 'state', 'type': 'select', 'required': True, 'label': 'State'},
                {'name': 'pincode', 'type': 'text', 'required': True, 'label': 'PIN Code'}
            ]
        }],
        'captcha_detected': True,
        'captcha_type': 'reCAPTCHA v2',
        'payment_detected': False,
        'language': language,
        'timestamp': datetime.utcnow().isoformat()
    }

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0-render',
        'indian_languages_supported': len(INDIAN_LANGUAGES),
        'deployment': 'render'
    })

@app.route('/api/v1/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_website():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    result = mock_analyze_url(data['url'], data.get('language', 'en'))
    memory_storage[result['session_id']] = {'form_structure': result}
    return jsonify(result), 200

@app.route('/api/v1/documents/extract', methods=['POST'])
def extract_document_data():
    return jsonify({
        'success': True,
        'extracted_data': {
            'full_name': 'राहुल कुमार',
            'email': 'rahul.kumar@example.com',
            'phone': '+91-98765-43210',
            'address': '123, MG Road, Bangalore',
            'state': 'Karnataka',
            'pincode': '560001'
        },
        'confidence': 0.95
    }), 200

@app.route('/api/v1/submit', methods=['POST'])
@limiter.limit("5 per minute")
def submit_form():
    return jsonify({
        'success': True,
        'reference_number': f"BHARAT-{uuid.uuid4().hex[:8].upper()}",
        'timestamp': datetime.utcnow().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
