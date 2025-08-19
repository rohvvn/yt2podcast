# Personal Podcast Creator

Transform YouTube videos into your own personal podcast feed. Each user gets their own curated collection of audio content that they can listen to on any podcast app.

## Features

- **Personal Podcast Feeds**: Each user gets their own unique RSS feed
- **YouTube Integration**: Download and convert any YouTube video to MP3
- **Web Dashboard**: Easy-to-use interface to manage your episodes
- **User Authentication**: Secure user accounts and personal content
- **Podcast App Compatible**: Works with Apple Podcasts, Spotify, Google Podcasts, and more
- **Automatic Conversion**: Videos are automatically converted to high-quality audio

## How It Works

1. **Sign Up**: Create a free account
2. **Add Videos**: Paste YouTube URLs to add videos to your podcast
3. **Get Your Feed**: Receive a personal RSS feed URL
4. **Subscribe**: Add your feed to any podcast app
5. **Listen Anywhere**: Enjoy your content on your phone, in your car, or while working out

## Installation

### Prerequisites

- Python 3.8+
- FFmpeg (for audio conversion)
- Git

### Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd YTPodcasts
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`

4. **Set environment variables** (optional):
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export FLASK_DEBUG="False"
   ```

5. **Run the application**:
   ```bash
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         python app.py
   ```

6. **Open your browser** and go to `http://localhost:5000`
   qq
## Usage

### For Users

1. **Register** for a free account
2. **Add YouTube videos** by pasting URLs in your dashboard
3. **Copy your RSS feed URL** from the dashboard
4. **Subscribe** to your feed in any podcast app:
   - Apple Podcasts: Add by URL
   - Spotify: Add by RSS feed
   - Google Podcasts: Add by RSS feed
   - Any other podcast app that supports RSS

### For Developers

The application consists of:

- **`app.py`**: Main Flask application with user management and podcast generation
- **`yt2podcast.py`**: Core YouTube download and conversion functionality
- **`templates/`**: HTML templates for the web interface
- **`config.py`**: Configuration settings
- **`requirements.txt`**: Python dependencies

## API Endpoints

- `GET /` - Landing page
- `GET /register` - User registration form
- `POST /register` - Create new user account
- `GET /login` - Login form
- `POST /login` - Authenticate user
- `GET /dashboard` - User dashboard (requires login)
- `POST /add_video` - Add YouTube video to user's podcast
- `GET /feed/<username>` - User's personal RSS feed
- `POST /delete_episode/<id>` - Delete episode from user's podcast

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: User's email address
- `password_hash`: Hashed password
- `created_at`: Account creation timestamp

### Episodes Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `title`: Episode title
- `description`: Episode description
- `duration`: Audio duration in seconds
- `filename`: Audio file name
- `file_size`: File size in bytes
- `video_url`: Original YouTube URL
- `audio_url`: Generated audio file URL
- `video_hash`: MD5 hash of video URL for deduplication

## Configuration

Edit `config.py` to customize:

- Database connection
- File upload limits
- YouTube download quality
- Podcast feed settings

## Deployment

### Development
```bash
python app.py
```

### Production
```bash
export FLASK_DEBUG=False
export SECRET_KEY="your-secure-secret-key"
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (coming soon)
```bash
docker build -t personal-podcast-creator .
docker run -p 5000:5000 personal-podcast-creator
```

## Security Features

- Password hashing with Werkzeug
- User authentication with Flask-Login
- File access control (users can only access their own episodes)
- CSRF protection
- Secure file serving

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues:

1. Check that FFmpeg is properly installed
2. Ensure all dependencies are installed
3. Check the application logs for error messages
4. Open an issue on GitHub

## Roadmap

- [ ] Batch video processing
- [ ] Audio quality options
- [ ] Episode scheduling
- [ ] Public podcast sharing
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] API rate limiting
- [ ] Cloud storage integration
