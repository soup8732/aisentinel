#!/usr/bin/env python3
"""
Generate sample sentiment data for dashboard testing.

This script creates mock data that mirrors the exact structure
produced by the real data collectors (Reddit, HackerNews, Twitter).

Output: data/processed/sentiment.csv

Usage:
    python scripts/generate_sample_data.py

After running, launch the dashboard to see the data:
    streamlit run src/dashboard/app.py
"""
import pandas as pd
from datetime import datetime, timedelta
import random
import os

# Create data directory if it doesn't exist
os.makedirs("data/processed", exist_ok=True)

# Tools and categories matching src/utils/taxonomy.py
# Category values: "text", "video_pic", "audio", "code"
TOOLS_DATA = [
    # Text & Chat (Category.TEXT = "text")
    ("ChatGPT", "text"),
    ("Claude", "text"),
    ("Gemini", "text"),
    ("DeepSeek", "text"),
    ("Mistral", "text"),
    ("Jasper", "text"),
    ("Copy.ai", "text"),
    ("Writesonic", "text"),
    ("Lindy", "text"),
    # Coding & Dev (Category.CODE = "code")
    ("GitHub Copilot", "code"),
    ("Amazon Q Developer", "code"),
    ("CodeWhisperer", "code"),
    ("Tabnine", "code"),
    ("Tabby", "code"),
    ("Replit Ghostwriter", "code"),
    ("Bolt", "code"),
    ("Loveable", "code"),
    ("JetBrains AI Assistant", "code"),
    ("Cursor", "code"),
    ("Codeium", "code"),
    ("Polycoder", "code"),
    ("AskCodi", "code"),
    ("Sourcery", "code"),
    ("Greta", "code"),
    # Image & Video (Category.VIDEO_PIC = "video_pic")
    ("Stability AI", "video_pic"),
    ("RunwayML", "video_pic"),
    ("Midjourney", "video_pic"),
    ("DALL-E", "video_pic"),
    ("DreamStudio", "video_pic"),
    ("OpenCV", "video_pic"),
    ("Adobe Firefly", "video_pic"),
    ("Pika Labs", "video_pic"),
    ("Luma Dream Machine", "video_pic"),
    ("Vidu", "video_pic"),
    # Audio & Speech (Category.AUDIO = "audio")
    ("Whisper", "audio"),
    ("ElevenLabs", "audio"),
    ("Murf AI", "audio"),
    ("PlayHT", "audio"),
    ("Speechify", "audio"),
    ("Synthesys", "audio"),
    ("Animaker", "audio"),
    ("Kits AI", "audio"),
    ("WellSaid Labs", "audio"),
    ("Hume", "audio"),
    ("DupDub", "audio"),
]

# Sample texts organized by sentiment
# Includes some privacy-related keywords to test privacy scoring
POSITIVE_TEXTS = [
    "Really impressed with the results from {tool}!",
    "{tool} has been a game changer for my workflow.",
    "Love using {tool} for my daily tasks. Highly recommend!",
    "The quality of {tool} output is consistently excellent.",
    "Been using {tool} for months now, absolutely worth it!",
    "{tool} saves me hours every week. Great investment.",
    "Just tried {tool} and wow, the accuracy is impressive.",
    "{tool} helped me finish my project in half the time.",
    "The latest update to {tool} made it even better.",
    "Customer support for {tool} was really helpful too.",
]

NEUTRAL_TEXTS = [
    "Trying out {tool}, seems okay so far.",
    "{tool} works fine for basic tasks.",
    "Mixed feelings about {tool}, has pros and cons.",
    "Using {tool} occasionally, it's decent.",
    "{tool} is fine but nothing spectacular.",
    "Still evaluating {tool} for our team.",
    "{tool} does what it says, nothing more.",
    "Switched from another tool to {tool}, similar experience.",
    "The free tier of {tool} is limited but usable.",
    "{tool} works but the UI could be better.",
]

NEGATIVE_TEXTS = [
    "Disappointed with {tool}, expected better quality.",
    "{tool} has too many limitations and bugs.",
    "Not worth the price. {tool} needs improvement.",
    "Having issues with {tool}, very frustrating.",
    "{tool} doesn't live up to the hype honestly.",
    "The output from {tool} is often inaccurate.",
    "{tool} keeps crashing, really unreliable.",
    "Cancelled my {tool} subscription. Not impressed.",
    "{tool} was slow and the results were mediocre.",
    "Would not recommend {tool} in its current state.",
]

# Privacy-related texts (for testing privacy score calculation)
PRIVACY_CONCERN_TEXTS = [
    "Worried about data privacy with {tool}.",
    "Is {tool} safe to use with sensitive data?",
    "Concerned about security when using {tool}.",
    "{tool} had a data breach recently, be careful.",
    "Not sure if {tool} is safe for confidential work.",
    "The privacy policy of {tool} is concerning.",
    "Don't trust {tool} with private information.",
    "Security issue reported with {tool} last week.",
]


def generate_sample_data(num_samples: int = 500) -> pd.DataFrame:
    """
    Generate mock sentiment data matching real collector output format.

    Args:
        num_samples: Number of sample records to generate

    Returns:
        DataFrame with columns: created_at, tool, category, score, label, text
    """
    data = []

    for i in range(num_samples):
        tool, category = random.choice(TOOLS_DATA)

        # Generate sentiment with realistic distribution
        # Popular tools skew positive, others more balanced
        sentiment_roll = random.random()

        if tool in ["ChatGPT", "Claude", "GitHub Copilot", "Midjourney"]:
            # Popular tools: 55% positive, 30% neutral, 15% negative
            if sentiment_roll < 0.55:
                label = "positive"
                score = random.uniform(0.25, 1.0)
            elif sentiment_roll < 0.85:
                label = "neutral"
                score = random.uniform(-0.2, 0.2)
            else:
                label = "negative"
                score = random.uniform(-1.0, -0.25)
        else:
            # Other tools: 40% positive, 35% neutral, 25% negative
            if sentiment_roll < 0.40:
                label = "positive"
                score = random.uniform(0.25, 0.95)
            elif sentiment_roll < 0.75:
                label = "neutral"
                score = random.uniform(-0.2, 0.2)
            else:
                label = "negative"
                score = random.uniform(-0.95, -0.25)

        # Generate timestamp within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        timestamp = datetime.utcnow() - timedelta(
            days=days_ago,
            hours=hours_ago,
            minutes=minutes_ago
        )

        # Select text based on sentiment
        # 10% chance of privacy-related text for negative/neutral
        if random.random() < 0.10 and label != "positive":
            text = random.choice(PRIVACY_CONCERN_TEXTS).format(tool=tool)
            # Privacy concerns tend to be more negative
            if label == "neutral":
                score = random.uniform(-0.3, 0.0)
        elif label == "positive":
            text = random.choice(POSITIVE_TEXTS).format(tool=tool)
        elif label == "neutral":
            text = random.choice(NEUTRAL_TEXTS).format(tool=tool)
        else:
            text = random.choice(NEGATIVE_TEXTS).format(tool=tool)

        data.append({
            "created_at": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "tool": tool,
            "category": category,
            "score": round(score, 4),
            "label": label,
            "text": text,
        })

    df = pd.DataFrame(data)
    df = df.sort_values("created_at", ascending=False).reset_index(drop=True)
    return df


if __name__ == "__main__":
    # Generate sample data
    df = generate_sample_data(500)

    # Save to CSV
    output_file = "data/processed/sentiment.csv"
    df.to_csv(output_file, index=False)

    print(f"Generated {len(df)} sample sentiment records")
    print(f"Saved to: {output_file}")
    print(f"\nTools included: {len(TOOLS_DATA)}")
    print(f"\nSentiment distribution:")
    print(df["label"].value_counts().to_string())
    print(f"\nCategory distribution:")
    print(df["category"].value_counts().to_string())
    print(f"\nDate range: {df['created_at'].min()} to {df['created_at'].max()}")
    print(f"\nRun 'streamlit run src/dashboard/app.py' to view the dashboard")
