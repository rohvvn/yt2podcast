#!/usr/bin/env python3
"""
Test script to verify yt2podcast setup and dependencies.
Run this before using the main application.
"""

import sys
import importlib

def test_imports():
    """Test if all required modules can be imported."""
    required_modules = [
        'yt_dlp',
        'feedgen',
        'argparse',
        'json',
        'hashlib',
        'datetime',
        'pathlib',
        'urllib.parse',
        'xml.etree.ElementTree'
    ]
    
    print("Testing imports...")
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nFailed to import: {', '.join(failed_imports)}")
        print("Please install missing dependencies:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All imports successful!")
        return True

def test_ffmpeg():
    """Test if FFmpeg is available."""
    import subprocess
    
    print("\nTesting FFmpeg...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ FFmpeg is available")
            return True
        else:
            print("✗ FFmpeg returned non-zero exit code")
            return False
    except FileNotFoundError:
        print("✗ FFmpeg not found in PATH")
        print("Please install FFmpeg:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        return False
    except subprocess.TimeoutExpired:
        print("✗ FFmpeg test timed out")
        return False

def test_yt2podcast_import():
    """Test if yt2podcast.py can be imported."""
    print("\nTesting yt2podcast.py...")
    try:
        # Add current directory to path
        import sys
        import os
        sys.path.insert(0, os.getcwd())
        
        # Try to import the main class
        from yt2podcast import YT2Podcast
        print("✓ yt2podcast.py imports successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import yt2podcast.py: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error importing yt2podcast.py: {e}")
        return False

def main():
    """Run all tests."""
    print("YT2Podcast Setup Test")
    print("=" * 30)
    
    tests = [
        test_imports,
        test_ffmpeg,
        test_yt2podcast_import
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 30)
    if all(results):
        print("✓ All tests passed! You're ready to use yt2podcast.")
        print("\nUsage example:")
        print('python yt2podcast.py "https://youtube.com/watch?v=someID"')
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main() 