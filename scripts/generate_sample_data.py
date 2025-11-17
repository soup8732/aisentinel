#!/usr/bin/env python3
"""Generate sample sentiment data for dashboard demo."""
import pandas as pd
from datetime import datetime, timedelta
import random
import os

# Create data directory if it doesn't exist
os.makedirs("data/processed", exist_ok=True)

# Sample AI tools from the taxonomy
tools_data = [
    ("ChatGPT", "text_and_chat"),
    ("Claude", "text_and_chat"),
    ("Gemini", "text_and_chat"),
    ("GitHub Copilot", "coding_and_dev"),
    ("Cursor", "coding_and_dev"),
    ("Tabnine", "coding_and_dev"),
    ("Midjourney", "images_and_video"),
    ("DALL-E", "images_and_video"),
    ("Whisper", "audio_and_speech"),
    ("ElevenLabs", "audio_and_speech"),
]

# Generate sample data
num_samples = 200
data = []

for _ in range(num_samples):
    tool, category = random.choice(tools_data)

    # Generate sentiment skewed towards positive for popular tools
    sentiment_roll = random.random()
    if tool in ["ChatGPT", "Claude", "GitHub Copilot"]:
        if sentiment_roll < 0.6:
            label = "positive"
            score = random.uniform(0.3, 1.0)
        elif sentiment_roll < 0.85:
            label = "neutral"
            score = random.uniform(-0.2, 0.3)
        else:
            label = "negative"
            score = random.uniform(-1.0, -0.2)
    else:
        if sentiment_roll < 0.45:
            label = "positive"
            score = random.uniform(0.2, 0.9)
        elif sentiment_roll < 0.75:
            label = "neutral"
            score = random.uniform(-0.3, 0.3)
        else:
            label = "negative"
            score = random.uniform(-0.9, -0.2)

    # Generate timestamp within last 30 days
    days_ago = random.randint(0, 30)
    timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

    # Generate sample text
    positive_texts = [
        f"{tool} is amazing! Really impressed with the results.",
        f"Love using {tool} for my daily work. Highly recommend!",
        f"{tool} has been a game changer for productivity.",
        f"The quality of {tool} output is consistently excellent.",
        f"Been using {tool} for months now, absolutely worth it!",
    ]

    neutral_texts = [
        f"Trying out {tool}, seems okay so far.",
        f"{tool} works fine for basic tasks.",
        f"Mixed feelings about {tool}, has pros and cons.",
        f"Using {tool} occasionally, it's decent.",
        f"{tool} is fine but nothing spectacular.",
    ]

    negative_texts = [
        f"Disappointed with {tool}, expected better quality.",
        f"{tool} has too many limitations and bugs.",
        f"Not worth the price. {tool} needs improvement.",
        f"Having issues with {tool}, very frustrating.",
        f"{tool} doesn't live up to the hype honestly.",
    ]

    if label == "positive":
        text = random.choice(positive_texts)
    elif label == "neutral":
        text = random.choice(neutral_texts)
    else:
        text = random.choice(negative_texts)

    data.append({
        "id": f"sample_{_}",
        "created_at": timestamp.isoformat(),
        "text": text,
        "tool": tool,
        "category": category,
        "label": label,
        "score": round(score, 3),
        "confidence": round(random.uniform(0.7, 0.99), 3),
        "source": "sample_data"
    })

# Create DataFrame and save
df = pd.DataFrame(data)
df = df.sort_values("created_at", ascending=False)

output_file = "data/processed/sentiment_results.csv"
df.to_csv(output_file, index=False)

print(f"✅ Generated {len(df)} sample sentiment records")
print(f"📁 Saved to: {output_file}")
print(f"\nTools included: {', '.join([t for t, _ in tools_data])}")
print(f"\nSentiment distribution:")
print(df["label"].value_counts())
print(f"\nDate range: {df['created_at'].min()} to {df['created_at'].max()}")
