"""Prepare training data for sentiment analysis model.

Downloads and preprocesses datasets for training a custom TensorFlow sentiment model.
Uses multiple sources to create a robust training set.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


def clean_text(text: str) -> str:
    """Clean and normalize text for sentiment analysis."""
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    # Remove mentions and hashtags (but keep the text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#(\w+)', r'\1', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text


def load_sst2_from_huggingface() -> pd.DataFrame:
    """Load Stanford Sentiment Treebank (SST-2) dataset from HuggingFace."""
    try:
        from datasets import load_dataset

        print("Loading SST-2 dataset from HuggingFace...")
        dataset = load_dataset("glue", "sst2")

        # Combine train and validation
        train_data = dataset["train"].to_pandas()
        val_data = dataset["validation"].to_pandas()

        df = pd.concat([train_data, val_data], ignore_index=True)

        # Map labels: 0=negative, 1=positive
        df["sentiment"] = df["label"].map({0: "negative", 1: "positive"})
        df["text"] = df["sentence"].apply(clean_text)
        df["source"] = "sst2"

        return df[["text", "sentiment", "source"]]
    except Exception as e:
        print(f"Could not load SST-2: {e}")
        return pd.DataFrame()


def load_imdb_dataset() -> pd.DataFrame:
    """Load IMDB movie reviews dataset."""
    try:
        from datasets import load_dataset

        print("Loading IMDB dataset from HuggingFace...")
        dataset = load_dataset("imdb")

        # Use a subset for faster training (10k samples)
        train_data = dataset["train"].select(range(10000)).to_pandas()
        test_data = dataset["test"].select(range(5000)).to_pandas()

        df = pd.concat([train_data, test_data], ignore_index=True)

        # Map labels: 0=negative, 1=positive
        df["sentiment"] = df["label"].map({0: "negative", 1: "positive"})
        df["text"] = df["text"].apply(clean_text)
        df["source"] = "imdb"

        return df[["text", "sentiment", "source"]]
    except Exception as e:
        print(f"Could not load IMDB: {e}")
        return pd.DataFrame()


def create_ai_tools_synthetic_data() -> pd.DataFrame:
    """Create synthetic AI tools review data for domain-specific training."""
    tools = [
        "ChatGPT", "Claude", "Gemini", "GitHub Copilot", "Midjourney",
        "DALL-E", "Stable Diffusion", "Whisper", "ElevenLabs", "DeepSeek"
    ]

    positive_templates = [
        "{tool} is amazing! It really helps with my workflow.",
        "I love using {tool}, it's so intuitive and powerful.",
        "{tool} has completely transformed how I work. Highly recommend!",
        "Best AI tool I've used. {tool} delivers every time.",
        "{tool} exceeded my expectations. Great results!",
        "Incredible performance from {tool}. Worth every penny.",
        "{tool} is a game changer for productivity.",
    ]

    negative_templates = [
        "{tool} is terrible. Doesn't work as advertised.",
        "Very disappointed with {tool}. Not worth it.",
        "{tool} has too many bugs and issues.",
        "I regret using {tool}. Poor quality outputs.",
        "{tool} is overhyped and underdelivers.",
        "Waste of money. {tool} is not reliable.",
        "{tool} needs major improvements. Frustrating experience.",
    ]

    neutral_templates = [
        "{tool} is okay, nothing special.",
        "Mixed feelings about {tool}. Some good, some bad.",
        "{tool} works but has room for improvement.",
        "Not sure about {tool} yet, still testing.",
        "{tool} is average compared to alternatives.",
    ]

    rows = []
    for tool in tools:
        # Generate positive samples
        for template in positive_templates * 5:  # 35 per tool
            rows.append({
                "text": template.format(tool=tool),
                "sentiment": "positive",
                "source": "synthetic_ai_tools"
            })

        # Generate negative samples
        for template in negative_templates * 5:  # 35 per tool
            rows.append({
                "text": template.format(tool=tool),
                "sentiment": "negative",
                "source": "synthetic_ai_tools"
            })

        # Generate neutral samples
        for template in neutral_templates * 2:  # 10 per tool
            rows.append({
                "text": template.format(tool=tool),
                "sentiment": "neutral",
                "source": "synthetic_ai_tools"
            })

    return pd.DataFrame(rows)


def prepare_training_data(
    output_dir: Path,
    include_sst2: bool = True,
    include_imdb: bool = True,
    include_synthetic: bool = True,
    test_size: float = 0.2,
    val_size: float = 0.1,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Prepare and split training data.

    Args:
        output_dir: Directory to save processed data
        include_sst2: Include Stanford Sentiment Treebank
        include_imdb: Include IMDB reviews
        include_synthetic: Include synthetic AI tools data
        test_size: Proportion of data for testing
        val_size: Proportion of training data for validation

    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    datasets = []

    if include_sst2:
        sst2_df = load_sst2_from_huggingface()
        if not sst2_df.empty:
            datasets.append(sst2_df)
            print(f"Loaded {len(sst2_df)} samples from SST-2")

    if include_imdb:
        imdb_df = load_imdb_dataset()
        if not imdb_df.empty:
            datasets.append(imdb_df)
            print(f"Loaded {len(imdb_df)} samples from IMDB")

    if include_synthetic:
        synthetic_df = create_ai_tools_synthetic_data()
        datasets.append(synthetic_df)
        print(f"Generated {len(synthetic_df)} synthetic AI tools samples")

    if not datasets:
        raise ValueError("No datasets loaded. Check your configuration.")

    # Combine all datasets
    combined_df = pd.concat(datasets, ignore_index=True)
    print(f"\nTotal samples: {len(combined_df)}")
    print(f"Sentiment distribution:\n{combined_df['sentiment'].value_counts()}")

    # Remove duplicates and null values
    combined_df = combined_df.drop_duplicates(subset=["text"])
    combined_df = combined_df.dropna(subset=["text", "sentiment"])
    combined_df = combined_df[combined_df["text"].str.len() > 10]  # Remove very short texts

    print(f"After cleaning: {len(combined_df)} samples")

    # Encode sentiment labels
    label_map = {"negative": 0, "neutral": 1, "positive": 2}
    combined_df["label"] = combined_df["sentiment"].map(label_map)

    # Split into train/val/test
    train_val_df, test_df = train_test_split(
        combined_df,
        test_size=test_size,
        random_state=42,
        stratify=combined_df["label"]
    )

    train_df, val_df = train_test_split(
        train_val_df,
        test_size=val_size,
        random_state=42,
        stratify=train_val_df["label"]
    )

    # Save to CSV
    train_df.to_csv(output_dir / "train.csv", index=False)
    val_df.to_csv(output_dir / "val.csv", index=False)
    test_df.to_csv(output_dir / "test.csv", index=False)

    print(f"\nDataset splits:")
    print(f"  Train: {len(train_df)} samples")
    print(f"  Val:   {len(val_df)} samples")
    print(f"  Test:  {len(test_df)} samples")

    # Save metadata
    metadata = {
        "total_samples": len(combined_df),
        "train_samples": len(train_df),
        "val_samples": len(val_df),
        "test_samples": len(test_df),
        "label_map": label_map,
        "sources": combined_df["source"].value_counts().to_dict(),
        "sentiment_distribution": combined_df["sentiment"].value_counts().to_dict(),
    }

    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nData saved to {output_dir}")
    return train_df, val_df, test_df


if __name__ == "__main__":
    import sys

    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))

    output_dir = project_root / "data" / "processed"

    print("Preparing training data...")
    print("=" * 60)

    train_df, val_df, test_df = prepare_training_data(
        output_dir=output_dir,
        include_sst2=True,
        include_imdb=True,
        include_synthetic=True,
    )

    print("\n" + "=" * 60)
    print("Data preparation complete!")
    print("\nNext steps:")
    print("  1. Run: python src/ml/train_model.py")
    print("  2. Evaluate model performance")
    print("  3. Deploy to production")
