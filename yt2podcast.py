#!/usr/bin/env python3
"""
yt2podcast - turns youtube videos into podcast episodes
pretty straightforward, just give it a URL and it does the rest

Usage:
    python yt2podcast.py "https://youtube.com/watch?v=someID"
"""

import argparse
import os
import sys
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
import yt_dlp
from feedgen.feed import FeedGenerator
import xml.etree.ElementTree as ET


class YT2Podcast:
    def __init__(self, base_url="https://rohvvn.github.io/yt2podcast"):
        self.base_url = base_url.rstrip('/')
        self.episodes_dir = Path("episodes")
        self.rss_file = Path("rss.xml")
        self.metadata_file = Path("episodes_metadata.json")
        
        # make sure episodes folder exists
        self.episodes_dir.mkdir(exist_ok=True)
        
        # load up existing metadata if any
        self.metadata = self._load_metadata()
    
    def _load_metadata(self):
        """load the metadata file if it exists"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_metadata(self):
        """save metadata back to file"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def _get_video_hash(self, url):
        """make a hash from the URL to track episodes"""
        return hashlib.md5(url.encode()).hexdigest()[:8]
    
    def _sanitize_filename(self, title):
        """clean up the title so it works as a filename"""
        import re
        # get rid of bad characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', title)
        # keep it reasonable length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized.strip()
    
    def download_video(self, url):
        """download the video and convert to mp3"""
        video_hash = self._get_video_hash(url)
        
        # see if we already have this one
        if video_hash in self.metadata:
            print(f"Video already downloaded: {self.metadata[video_hash]['title']}")
            return self.metadata[video_hash]
        
        print(f"Downloading video from: {url}")
        
        # setup yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': str(self.episodes_dir / '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # grab video info first
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                description = info.get('description', '')
                duration = info.get('duration', 0)
                upload_date = info.get('upload_date', '')
                uploader = info.get('uploader', 'Unknown')
                
                # actually download it
                ydl.download([url])
                
                # figure out what the file got named
                sanitized_title = self._sanitize_filename(title)
                mp3_filename = f"{sanitized_title}.mp3"
                mp3_path = self.episodes_dir / mp3_filename
                
                # sometimes the filename is different, so find the actual file
                if not mp3_path.exists():
                    mp3_files = list(self.episodes_dir.glob("*.mp3"))
                    if mp3_files:
                        # just grab the newest one
                        mp3_path = max(mp3_files, key=lambda x: x.stat().st_mtime)
                        mp3_filename = mp3_path.name
                
                if not mp3_path.exists():
                    raise FileNotFoundError("Downloaded MP3 file not found")
                
                # save all the episode info
                episode_data = {
                    'title': title,
                    'description': description[:500] + '...' if len(description) > 500 else description,
                    'duration': duration,
                    'upload_date': upload_date,
                    'uploader': uploader,
                    'filename': mp3_filename,
                    'file_size': mp3_path.stat().st_size,
                    'download_date': datetime.now(timezone.utc).isoformat(),
                    'video_url': url,
                    'audio_url': f"{self.base_url}/episodes/{mp3_filename}",
                }
                
                # stash it away
                self.metadata[video_hash] = episode_data
                self._save_metadata()
                
                print(f"Successfully downloaded: {title}")
                print(f"File saved as: {mp3_filename}")
                
                return episode_data
                
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None
    
    def generate_rss_feed(self):
        """make the RSS feed for podcast apps"""
        fg = FeedGenerator()
        fg.load_extension('podcast')
        
        # basic podcast info
        fg.title('My YouTube Podcast')
        fg.description('A podcast feed generated from YouTube videos')
        fg.link(href=f"{self.base_url}/rss.xml", rel='self')
        fg.language('en')
        fg.author(name='YT2Podcast', email='noreply@example.com')
        fg.subtitle('YouTube videos as podcast episodes')
        # fg.category('Technology')  # Commented out due to feedgen compatibility issues
        # fg.explicit('false')      # Commented out due to feedgen compatibility issues
        
        # add each episode to the feed
        for video_hash, episode_data in self.metadata.items():
            fe = fg.add_entry()
            fe.title(episode_data['title'])
            fe.description(episode_data['description'])
            fe.link(href=episode_data['audio_url'])
            
            # figure out when this was published
            if episode_data['upload_date']:
                try:
                    # youtube uses YYYYMMDD format
                    upload_date = datetime.strptime(episode_data['upload_date'], '%Y%m%d')
                    upload_date = upload_date.replace(tzinfo=timezone.utc)
                    fe.published(upload_date)
                except ValueError:
                    # fallback to when we downloaded it
                    download_date = datetime.fromisoformat(episode_data['download_date'])
                    fe.published(download_date)
            else:
                download_date = datetime.fromisoformat(episode_data['download_date'])
                fe.published(download_date)
            
            # podcast-specific stuff (commented out due to feedgen being weird)
            # fe.podcast.itunes_author(episode_data['uploader'])
            # fe.podcast.itunes_duration(self._format_duration(episode_data['duration']))
            # fe.podcast.itunes_explicit('false')
            
            # this is the actual audio file link
            fe.enclosure(episode_data['audio_url'], str(episode_data['file_size']), 'audio/mpeg')
        
        # write it all out
        fg.rss_file(str(self.rss_file))
        print(f"RSS feed generated: {self.rss_file}")
    
    def _format_duration(self, seconds):
        """turn seconds into HH:MM:SS format"""
        if not seconds:
            return "00:00:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def process_video(self, url):
        """main function that does everything"""
        print(f"Processing YouTube URL: {url}")
        
        # grab the video
        episode_data = self.download_video(url)
        if not episode_data:
            print("Failed to download video")
            return False
        
        # make the RSS feed
        self.generate_rss_feed()
        
        print(f"\nPodcast episode added successfully!")
        print(f"Title: {episode_data['title']}")
        print(f"Audio URL: {episode_data['audio_url']}")
        print(f"RSS Feed: {self.base_url}/rss.xml")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description='turn youtube videos into podcast episodes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python yt2podcast.py "https://youtube.com/watch?v=someID"
  python yt2podcast.py --base-url "https://mypodcast.com" "https://youtube.com/watch?v=someID"
        """
    )
    
    parser.add_argument(
        'url',
        help='youtube video URL to download'
    )
    
    parser.add_argument(
        '--base-url',
        default='https://rohvvn.github.io/yt2podcast',
        help='base URL for the podcast feed (default: https://rohvvn.github.io/yt2podcast)'
    )
    
    args = parser.parse_args()
    
    # make sure it's actually a URL
    if not args.url.startswith(('http://', 'https://')):
        print("Error: Please provide a valid URL starting with http:// or https://")
        sys.exit(1)
    
    # do the thing
    yt2podcast = YT2Podcast(base_url=args.base_url)
    
    try:
        success = yt2podcast.process_video(args.url)
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 