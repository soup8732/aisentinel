#!/usr/bin/env python3
"""Collect Twitter data and save to processed CSV for dashboard."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.data_collection.twitter_collector import TwitterCollector
from src.sentiment_analysis.analyzer import AdvancedSentimentAnalyzer
from src.utils.config import load_config

if __name__ == "__main__":
    cfg = load_config()
    if not cfg.apis.twitter_bearer_token:
        print("❌ TWITTER_BEARER_TOKEN not found in .env")
        exit(1)
    
    print("Collecting tweets about AI tools...")
    
    # Collect tweets
    collector = TwitterCollector(limit=100)
    raw_data = list(collector.collect())
    
    if not raw_data:
        print("⚠️  No tweets collected. Check your API key and rate limits.")
        exit(1)
    
    print(f"✅ Collected {len(raw_data)} tweets")
    
    # Analyze sentiment
    print("Analyzing sentiment...")
    analyzer = AdvancedSentimentAnalyzer()
    
    df = pd.DataFrame(raw_data)
    df["sentiment_result"] = df["text"].apply(lambda x: analyzer.analyze(str(x)))
    df["score"] = df["sentiment_result"].apply(lambda x: x.score)
    df["label"] = df["sentiment_result"].apply(lambda x: x.label)
    
    # Ensure required columns
    df = df.rename(columns={"created_at": "created_at"})
    if "tool" not in df.columns:
        df["tool"] = None
    if "category" not in df.columns:
        df["category"] = None
    
    # Save to processed data
    output_path = cfg.paths.processed_dir / "sentiment.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Merge with existing data if present
    if output_path.exists():
        existing = pd.read_csv(output_path)
        df = pd.concat([existing, df], ignore_index=True)
        df = df.drop_duplicates(subset=["id"], keep="last")
    
    df.to_csv(output_path, index=False)
    print(f"✅ Saved {len(df)} records to {output_path}")
    print(f"   Dashboard will now show this data!")

