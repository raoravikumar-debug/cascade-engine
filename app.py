#!/usr/bin/env python3
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic

app = Flask(__name__, static_folder='build', static_url_path='')
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    else:
        return app.send_static_file('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/analyze', methods=['POST'])
def analyze_cascade():
    try:
        data = request.json
        event = data.get('event', '')
        magnitude = data.get('magnitude', 'Moderate (5-10%)')
        duration = data.get('duration', 'Medium (8-16w)')
        
        if not event:
            return jsonify({'error': 'Missing event parameter'}), 400
        
        prompt = f"""Analyze this economic event for India with deep cascade effects:

Event: {event}
Magnitude: {magnitude}
Duration: {duration}

Provide analysis with:
1. TIMELINE & LEADING INDICATORS
2. RBI POLICY PREDICTION
3. SECTOR IMPACT ANALYSIS
4. HIDDEN RIPPLES & CROSS-CUTTING THEMES
5. SCENARIO PROBABILITIES

Be specific with data. Question assumptions."""

        message = client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = message.content[0].text
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'event': event,
            'magnitude': magnitude,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    templates = {
        "LPG Crisis India 2026": {
            "event": "LPG crisis India 2026",
            "magnitude": "Extreme (20%+)",
            "duration": "Prolonged (16+w)",
            "description": "Strait of Hormuz disruption"
        }
    }
    return jsonify(templates)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
