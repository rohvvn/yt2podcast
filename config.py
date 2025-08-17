#!/usr/bin/env python3
"""
Configuration file for Personal Podcast Creator
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

# Database configuration
DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///podcast_users.db')

# File storage
UPLOAD_FOLDER = BASE_DIR / 'user_episodes'
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size

# YouTube download settings
YT_DLP_OPTIONS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': False,
    'no_warnings': False,
}

# Podcast feed settings
PODCAST_CATEGORY = 'Personal'
PODCAST_LANGUAGE = 'en'
PODCAST_EXPLICIT = 'false' 