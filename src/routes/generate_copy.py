from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import json

generate_copy_bp = Blueprint('generate_copy', __name__)

@generate_copy_bp.route('/generate-copy', methods=['POST'])
@cross_origin()
def generate_copy():
    """Generate ad copy based on user prompt"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        prompt = data.get('prompt', '')
        num_variations = data.get('num_variations', 3)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate ad copy variations (placeholder logic for now)
        variations = []
        for i in range(num_variations):
            variation = f"""🚀 Ad Copy Variation {i+1}:

Headline: Transform Your Business with {prompt}
Body: Discover the power of innovation! Our cutting-edge solution helps you achieve remarkable results. Join thousands of satisfied customers who have already transformed their business.
Call-to-Action: Get Started Today - Limited Time Offer!

Target: Perfect for businesses looking to enhance their {prompt} strategy."""
            variations.append(variation)
        
        return jsonify({
            'success': True,
            'variations': variations,
            'prompt': prompt,
            'count': len(variations)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'success': False
        }), 500

@generate_copy_bp.route('/generate-copy', methods=['GET'])
@cross_origin()
def generate_copy_info():
    """Info endpoint for the generate copy API"""
    return jsonify({
        'message': 'NeonAdsAi Copy Generation API',
        'description': 'Send a POST request with prompt and num_variations to generate ad copy',
        'example': {
            'prompt': 'fitness app for busy professionals',
            'num_variations': 3
        }
    }), 200

