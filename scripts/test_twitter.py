#!/usr/bin/env python3
"""Test Twitter collector with bearer token."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection.twitter_collector import TwitterCollector
from src.utils.config import load_config

if __name__ == "__main__":
    cfg = load_config()
    if not cfg.apis.twitter_bearer_token:
        print("❌ TWITTER_BEARER_TOKEN not found in .env")
        exit(1)
    
    print("✅ Bearer token found!")
    print("Testing Twitter collector...")
    
    collector = TwitterCollector(query_terms=["ChatGPT", "Claude"], limit=5)
    data = list(collector.collect())
    
    print(f"✅ Collected {len(data)} tweets")
    if data:
        print("\nSample tweet:")
        print(f"  Tool: {data[0].get('tool', 'N/A')}")
        print(f"  Text: {data[0].get('text', '')[:100]}...")
        print(f"  Score: {data[0].get('score', 'N/A')}")
    else:
        print("⚠️  No tweets collected. Check your API key and rate limits.")

