#!/usr/bin/env python3
"""
Simple wrapper to run Flask app without debug mode and reloader.
"""
import os

# Ensure debug mode is off
os.environ['FLASK_DEBUG'] = '0'

from app import app

if __name__ == '__main__':
    # Disable debug mode explicitly
    app.debug = False
    print(f"Starting Flask with debug={app.debug}")
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
