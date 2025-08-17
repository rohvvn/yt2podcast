#!/usr/bin/env python3
"""
Test CSRF token generation
"""

from app import app

with app.app_context():
    from flask_wtf.csrf import generate_csrf
    
    # Test CSRF token generation
    token = generate_csrf()
    print(f"CSRF Token generated: {token}")
    print(f"Token length: {len(token)}")
    print("✅ CSRF tokens are working!") 