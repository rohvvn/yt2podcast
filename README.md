# YT2Podcast

A Python CLI tool that downloads YouTube videos as MP3s and generates podcast RSS feeds. Perfect for creating your own podcast from YouTube content.

## Features

- Download YouTube videos as high-quality MP3 files
- Generate RSS feeds compatible with podcast apps
- Automatic episode metadata extraction
- Duplicate detection to avoid re-downloading
- Hostable on GitHub Pages or any static site
- Single-file application for easy deployment

## Installation

### Prerequisites

1. **Python 3.7+** - Make sure you have Python installed
2. **FFmpeg** - Required for audio conversion
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python yt2podcast.py "https://youtube.com/watch?v=someID"
```

### Custom Base URL

```bash
python yt2podcast.py --base-url "https://mypodcast.com" "https://youtube.com/watch?v=someID"
```

### Help

```bash
python yt2podcast.py --help
```

## How It Works

1. **Download**: Uses `yt-dlp` to download YouTube videos as MP3 files
2. **Store**: Saves MP3s in the `episodes/` directory
3. **Metadata**: Extracts and stores episode information (title, description, duration, etc.)
4. **RSS Feed**: Generates/updates `rss.xml` with podcast-compatible format
5. **Duplicate Detection**: Prevents re-downloading the same video

## File Structure

After running the tool, you'll have:

```
your-project/
├── yt2podcast.py          # Main application
├── requirements.txt        # Python dependencies
├── rss.xml               # Generated podcast feed
├── episodes_metadata.json # Episode metadata cache
└── episodes/             # Downloaded MP3 files
    ├── video1.mp3
    ├── video2.mp3
    └── ...
```

## Hosting on GitHub Pages

1. **Upload Files**: Push your files to a GitHub repository
2. **Enable Pages**: Go to Settings → Pages → Source → Deploy from a branch
3. **Update Base URL**: Use your GitHub Pages URL:
   ```bash
   python yt2podcast.py --base-url "https://yourusername.github.io/yourrepo" "https://youtube.com/watch?v=someID"
   ```

## RSS Feed Structure

The generated `rss.xml` includes:

- **Feed Metadata**: Title, description, language, author
- **Episode Entries**: Title, description, audio URL, publication date
- **Podcast Extensions**: iTunes-compatible tags for duration, author, etc.
- **Audio Enclosures**: Direct links to MP3 files

## Example RSS Feed

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>My YouTube Podcast</title>
    <description>A podcast feed generated from YouTube videos</description>
    <link>https://mydomain.com/rss.xml</link>
    <language>en</language>
    <itunes:author>YT2Podcast</itunes:author>
    <itunes:explicit>false</itunes:explicit>
    <item>
      <title>Video Title</title>
      <description>Video description...</description>
      <link>https://mydomain.com/episodes/video.mp3</link>
      <enclosure url="https://mydomain.com/episodes/video.mp3" length="1234567" type="audio/mpeg"/>
      <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
      <itunes:duration>10:30</itunes:duration>
      <itunes:author>Channel Name</itunes:author>
    </item>
  </channel>
</rss>
```

## Podcast App Compatibility

The generated RSS feed is compatible with:

- **Apple Podcasts**
- **Spotify**
- **Google Podcasts**
- **Pocket Casts**
- **Overcast**
- **And many more...**

## Configuration

### Customizing Feed Metadata

Edit the `generate_rss_feed()` method in `yt2podcast.py` to customize:

- Podcast title and description
- Author information
- Category and language
- Logo URL

### Audio Quality

Modify the `ydl_opts` in `download_video()` to change:

- Audio codec (mp3, m4a, etc.)
- Quality settings
- Output format

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Install FFmpeg and ensure it's in your PATH
2. **Download fails**: Check your internet connection and video availability
3. **Permission errors**: Ensure write permissions in the current directory
4. **Invalid URL**: Make sure the YouTube URL is correct and accessible

### Error Messages

- `"Error downloading video"`: Usually network or video availability issues
- `"Downloaded MP3 file not found"`: FFmpeg conversion failed
- `"Video already downloaded"`: Normal behavior for duplicate URLs

## Legal Considerations

- **Copyright**: Only download content you have permission to use
- **Terms of Service**: Respect YouTube's terms of service
- **Fair Use**: Consider fair use guidelines for your jurisdiction
- **Attribution**: Always credit original creators when possible

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source. Use responsibly and in accordance with applicable laws and terms of service. 