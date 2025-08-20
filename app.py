#!/usr/bin/env python3
"""
Multi-User YouTube to Podcast Platform
Each user gets their own personal RSS feed of YouTube videos
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
import json
import hashlib
from urllib.parse import urljoin

# Import your existing YT2Podcast functionality
from yt2podcast import YT2Podcast

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///podcast_users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup database
db = SQLAlchemy(app)

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Setup CSRF protection
csrf = CSRFProtect(app)

# Create uploads directory
UPLOAD_FOLDER = Path('user_episodes')
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    episodes = db.relationship('Episode', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer)  # in seconds
    upload_date = db.Column(db.String(20))  # YouTube upload date
    uploader = db.Column(db.String(100))
    filename = db.Column(db.String(200))
    file_size = db.Column(db.Integer)
    download_date = db.Column(db.DateTime, default=datetime.utcnow)
    video_url = db.Column(db.String(500))
    audio_url = db.Column(db.String(500))
    video_hash = db.Column(db.String(16), unique=True)  # MD5 hash of video URL

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    episodes = Episode.query.filter_by(user_id=current_user.id).order_by(Episode.download_date.desc()).all()
    return render_template('dashboard.html', episodes=episodes)

@app.route('/add_video', methods=['POST'])
@login_required
def add_video():
    video_url = request.form['video_url']
    
    if not video_url.startswith(('http://', 'https://')):
        flash('Please provide a valid URL')
        return redirect(url_for('dashboard'))
    
    # Check if video already exists for this user
    video_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
    existing_episode = Episode.query.filter_by(video_hash=video_hash, user_id=current_user.id).first()
    
    if existing_episode:
        flash('This video is already in your podcast!')
        return redirect(url_for('dashboard'))
    
    try:
        print(f"Starting download for user {current_user.username}: {video_url}")
        
        # Create user-specific episodes directory
        user_episodes_dir = UPLOAD_FOLDER / str(current_user.id)
        user_episodes_dir.mkdir(exist_ok=True)
        print(f"Created user directory: {user_episodes_dir}")
        
        # Download video using your existing YT2Podcast class
        base_url = request.host_url.rstrip('/')
        yt2podcast = YT2Podcast(base_url=base_url)
        yt2podcast.episodes_dir = user_episodes_dir
        
        print(f"Starting YT2Podcast download...")
        episode_data = yt2podcast.download_video(video_url)
        
        if episode_data:
            print(f"Download successful: {episode_data['title']}")
            
            # Save episode to database
            episode = Episode(
                user_id=current_user.id,
                title=episode_data['title'],
                description=episode_data['description'],
                duration=episode_data['duration'],
                upload_date=episode_data['upload_date'],
                uploader=episode_data['uploader'],
                filename=episode_data['filename'],
                file_size=episode_data['file_size'],
                video_url=video_url,
                audio_url=f"{base_url}/episode/{current_user.id}/{episode_data['filename']}",
                video_hash=video_hash
            )
            
            db.session.add(episode)
            db.session.commit()
            
            flash(f'Successfully added: {episode_data["title"]}')
            print(f"Episode saved to database with ID: {episode.id}")
        else:
            print("Download failed - no episode data returned")
            flash('Failed to download video - please check the URL and try again')
            
    except Exception as e:
        print(f"Error during video processing: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error processing video: {str(e)}')
    
    return redirect(url_for('dashboard'))

@app.route('/episode/<int:user_id>/<filename>')
def serve_episode(user_id, filename):
    """Serve audio files for podcast apps (no authentication required)"""
    user_episodes_dir = UPLOAD_FOLDER / str(user_id)
    audio_file = user_episodes_dir / filename
    
    if not audio_file.exists():
        return "File not found", 404
    
    # Set proper headers for podcast apps
    response = send_from_directory(user_episodes_dir, filename)
    response.headers['Content-Type'] = 'audio/mpeg'
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
    
    return response

@app.route('/feed/<username>')
def user_feed(username):
    """Generate personal RSS feed for a user (public access)"""
    user = User.query.filter_by(username=username).first()
    if not user:
        return "User not found", 404
    
    episodes = Episode.query.filter_by(user_id=user.id).order_by(Episode.download_date.desc()).all()
    
    # Generate RSS feed using your existing code
    from feedgen.feed import FeedGenerator
    
    fg = FeedGenerator()
    fg.load_extension('podcast')
    
    # Basic podcast info
    fg.title(f'{username}\'s Personal Podcast')
    fg.description(f'A personal podcast feed for {username}')
    fg.link(href=request.url, rel='self')
    fg.language('en')
    fg.author(name=username)
    fg.subtitle(f'YouTube videos curated by {username}')
    
    # Add podcast-specific metadata
    fg.category({'term': 'Personal', 'scheme': 'https://itunes.apple.com/us/genre/podcasts-personal/id1305'})
    # fg.podcast.itunes_explicit(False)  # Commented out due to validation issues
    
    # Add each episode
    for episode in episodes:
        fe = fg.add_entry()
        fe.title(episode.title)
        fe.description(episode.description)
        fe.link(href=episode.audio_url)
        
        # Set publication date
        if episode.upload_date:
            try:
                upload_date = datetime.strptime(episode.upload_date, '%Y%m%d')
                upload_date = upload_date.replace(tzinfo=timezone.utc)
                fe.published(upload_date)
            except ValueError:
                # Ensure download_date has timezone info
                if episode.download_date.tzinfo is None:
                    download_date = episode.download_date.replace(tzinfo=timezone.utc)
                else:
                    download_date = episode.download_date
                fe.published(download_date)
        else:
            # Ensure download_date has timezone info
            if episode.download_date.tzinfo is None:
                download_date = episode.download_date.replace(tzinfo=timezone.utc)
            else:
                download_date = episode.download_date
            fe.published(download_date)
        
        # Podcast metadata
        fe.podcast.itunes_author(episode.uploader or 'Unknown')
        fe.podcast.itunes_duration(_format_duration(episode.duration))
        # fe.podcast.itunes_explicit('false')  # Commented out due to validation issues
        fe.podcast.itunes_summary(episode.description)
        
        # Audio file enclosure
        fe.enclosure(episode.audio_url, str(episode.file_size), 'audio/mpeg')
    
    # Return RSS as XML
    response = app.response_class(fg.rss_str(), mimetype='application/rss+xml')
    return response

def _format_duration(seconds):
    """Format duration in HH:MM:SS format"""
    if not seconds:
        return "00:00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

@app.route('/delete_episode/<int:episode_id>', methods=['POST'])
@login_required
def delete_episode(episode_id):
    """Delete an episode from user's podcast"""
    episode = Episode.query.get_or_404(episode_id)
    
    if episode.user_id != current_user.id:
        flash('Unauthorized')
        return redirect(url_for('dashboard'))
    
    # Delete audio file
    user_episodes_dir = UPLOAD_FOLDER / str(current_user.id)
    audio_file = user_episodes_dir / episode.filename
    if audio_file.exists():
        audio_file.unlink()
    
    # Delete from database
    db.session.delete(episode)
    db.session.commit()
    
    flash('Episode deleted successfully')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Get port from environment variable (for production) or use 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 