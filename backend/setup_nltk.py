#!/usr/bin/env python3
"""
Setup script to download required NLTK data for sentiment analysis.
Run this once before starting the application.
"""

import nltk
import sys

def download_nltk_data():
    """Download required NLTK data files."""
    print("Setting up NLTK data for sentiment analysis...")
    
    try:
        # Download VADER lexicon
        print("Downloading VADER sentiment lexicon...")
        nltk.download('vader_lexicon', quiet=False)
        print("✓ VADER lexicon downloaded successfully")
        
        print("\n✅ All NLTK data downloaded successfully!")
        print("You can now start the application.")
        return 0
    except Exception as e:
        print(f"\n❌ Error downloading NLTK data: {e}")
        print("Please ensure you have internet connectivity and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(download_nltk_data())
