#!/usr/bin/env python3
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import anthropic

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# Serve index.html for root path
@app.route('/')
def serve_index():
    return send_file('index.html')

# API endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/analyze', methods=['POST'])
def analyze_cascade():
    """Main analysis endpoint - calls Claude API"""
    try:
        data = request.json
        event = data.get('event', '')
        magnitude = data.get('magnitude', 'Moderate (5-10%)')
        duration = data.get('duration', 'Medium (8-16w)')
        
        if not event:
            return jsonify({'error': 'Missing event parameter'}), 400
        
        # Build the analysis prompt
        prompt = f"""Analyze this economic event for India with deep cascade effects:

Event: {event}
Magnitude: {magnitude}
Duration: {duration}

Provide analysis with:
1. TIMELINE & LEADING INDICATORS (Immediate 0-2w, Short-term 2-8w, Medium-term 8-16w)
2. RBI POLICY PREDICTION (probability, timing, reasoning)
3. SECTOR IMPACT ANALYSIS (top 3-5 sectors affected)
4. HIDDEN RIPPLES & CROSS-CUTTING THEMES
5. SCENARIO PROBABILITIES (base case, bull case, bear case)

Be specific with data. Question your assumptions. Include non-obvious economic linkages."""

        # Call Claude API
        message = client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
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
    
    except anthropic.APIError as e:
        return jsonify({'error': f'Claude API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Return preset analysis templates"""
    templates = {
        "LPG Crisis India 2026": {
            "event": "LPG crisis India 2026",
            "magnitude": "Extreme (20%+)",
            "duration": "Prolonged (16+w)",
            "description": "Strait of Hormuz disruption driving 4x LPG price increase"
        }
    }
    return jsonify(templates)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
