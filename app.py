#!/usr/bin/env python3
"""
NeonAdsAi Backend Application
Entry point for deployment
"""

import os
import sys

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Import the Flask app from main.py
from main import app

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    
    # Debug mode based on environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"Starting neonadsai backend on port {port} (debug: {debug_mode})")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

