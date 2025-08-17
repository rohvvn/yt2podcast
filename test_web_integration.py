#!/usr/bin/env python3
"""
Test script to verify YT2Podcast integration with the web app
"""

import sys
from pathlib import Path
from yt2podcast import YT2Podcast

def test_yt2podcast():
    """Test the YT2Podcast class functionality"""
    print("Testing YT2Podcast integration...")
    
    # Create test directory
    test_dir = Path("test_downloads")
    test_dir.mkdir(exist_ok=True)
    
    # Test URL (a short video for testing)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short video
    
    try:
        # Initialize YT2Podcast
        yt2podcast = YT2Podcast(base_url="http://localhost:5000")
        yt2podcast.episodes_dir = test_dir
        
        print(f"Testing with URL: {test_url}")
        print(f"Output directory: {test_dir}")
        
        # Try to download
        episode_data = yt2podcast.download_video(test_url)
        
        if episode_data:
            print("✅ Download successful!")
            print(f"Title: {episode_data['title']}")
            print(f"Duration: {episode_data['duration']} seconds")
            print(f"Filename: {episode_data['filename']}")
            print(f"File size: {episode_data['file_size']} bytes")
            
            # Check if file exists
            file_path = test_dir / episode_data['filename']
            if file_path.exists():
                print(f"✅ Audio file created: {file_path}")
                print(f"File size on disk: {file_path.stat().st_size} bytes")
            else:
                print(f"❌ Audio file not found: {file_path}")
        else:
            print("❌ Download failed - no episode data returned")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test files
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
            print("Cleaned up test directory")

if __name__ == "__main__":
    test_yt2podcast() 