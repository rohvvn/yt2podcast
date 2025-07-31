# yt2podcast

Turn YouTube videos into podcast episodes. Just give it a URL and it downloads the audio, saves it as MP3, and creates an RSS feed.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install FFmpeg (required for audio conversion):
   - Windows: Download from ffmpeg.org
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

3. Run it:
```bash
python yt2podcast.py "https://youtube.com/watch?v=someID"
```

## What it m

- Downloads YouTube videos as MP3 files
- Saves them in an `episodes/` folder
- Creates/updates an RSS feed (`rss.xml`)
- Works with podcast apps like Apple Podcasts, Spotify, etc.

## Hosting on GitHub Pages

1. Push your files to GitHub
2. Enable Pages in repository settings
3. Use your GitHub Pages URL as the base URL:
```bash
python yt2podcast.py --base-url "https://username.github.io/repo" "YOUR_URL"
```

## Files created

- `episodes/` - MP3 files
- `rss.xml` - Podcast feed
- `episodes_metadata.json` - Episode info

That's it! Pretty simple.
