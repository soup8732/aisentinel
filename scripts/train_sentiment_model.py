#!/usr/bin/env python3
"""End-to-end pipeline for training sentiment analysis model.

This script:
1. Prepares training data from multiple sources
2. Trains a custom TensorFlow model
3. Evaluates and saves the model
4. Generates visualizations and metrics

Usage:
    python scripts/train_sentiment_model.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Run the complete training pipeline."""
    print("=" * 70)
    print("AISentinel - Complete Model Training Pipeline")
    print("=" * 70)

    # Step 1: Prepare training data
    print("\n[Step 1/3] Preparing training data...")
    print("-" * 70)

    from src.data_collection.prepare_training_data import prepare_training_data

    data_dir = PROJECT_ROOT / "data" / "processed"

    try:
        train_df, val_df, test_df = prepare_training_data(
            output_dir=data_dir,
            include_sst2=True,
            include_imdb=True,
            include_synthetic=True,
        )
        print(f"✓ Data preparation complete!")
    except Exception as e:
        print(f"✗ Error preparing data: {e}")
        print("\nNote: You may need to install additional dependencies:")
        print("  pip install datasets")
        return

    # Step 2: Train model
    print("\n[Step 2/3] Training sentiment model...")
    print("-" * 70)

    from src.ml.train_model import main as train_main

    try:
        train_main()
        print(f"✓ Model training complete!")
    except Exception as e:
        print(f"✗ Error training model: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 3: Summary
    print("\n[Step 3/3] Training Summary")
    print("-" * 70)
    print("✓ All steps completed successfully!")
    print("\nGenerated files:")
    print(f"  - Training data: {data_dir}")
    print(f"  - Trained model: {PROJECT_ROOT / 'models'}")
    print("\nNext steps:")
    print("  1. Review model metrics in models/run_*/metrics.json")
    print("  2. Check visualizations (training_history.png, confusion_matrix.png)")
    print("  3. Update src/sentiment_analysis/analyzer.py to use the trained model")
    print("  4. Test with: python scripts/test_model.py")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
