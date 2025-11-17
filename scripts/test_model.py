#!/usr/bin/env python3
"""Test trained sentiment model with real AI tool reviews.

This script:
1. Loads the latest trained model
2. Tests it on sample AI tool reviews
3. Compares predictions across different sentiment scenarios
4. Generates a test report
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def get_latest_model() -> Path:
    """Find the most recently trained model."""
    models_dir = PROJECT_ROOT / "models"
    if not models_dir.exists():
        raise FileNotFoundError(f"Models directory not found: {models_dir}")

    # Find all run directories
    run_dirs = sorted([d for d in models_dir.iterdir() if d.is_dir() and d.name.startswith("run_")])

    if not run_dirs:
        raise FileNotFoundError("No trained models found. Run train_sentiment_model.py first.")

    latest_run = run_dirs[-1]
    model_path = latest_run / "sentiment_model.keras"

    if not model_path.exists():
        # Try checkpoint
        model_path = latest_run / "checkpoints" / "best_model.keras"

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found in {latest_run}")

    return model_path


def get_test_reviews() -> List[Dict[str, str]]:
    """Get sample AI tool reviews for testing."""
    return [
        # Positive reviews
        {
            "text": "ChatGPT is absolutely amazing! It helps me write code so much faster.",
            "expected": "positive",
            "tool": "ChatGPT"
        },
        {
            "text": "Claude is incredible for complex reasoning tasks. Love using it!",
            "expected": "positive",
            "tool": "Claude"
        },
        {
            "text": "GitHub Copilot has transformed my coding workflow. Highly recommend!",
            "expected": "positive",
            "tool": "GitHub Copilot"
        },
        {
            "text": "Midjourney creates stunning images. Best AI art tool I've used.",
            "expected": "positive",
            "tool": "Midjourney"
        },
        {
            "text": "ElevenLabs voice quality is unmatched. Really impressive technology.",
            "expected": "positive",
            "tool": "ElevenLabs"
        },

        # Negative reviews
        {
            "text": "ChatGPT keeps making mistakes and giving wrong information. Very frustrating.",
            "expected": "negative",
            "tool": "ChatGPT"
        },
        {
            "text": "Disappointed with Claude. It's slow and often refuses to help.",
            "expected": "negative",
            "tool": "Claude"
        },
        {
            "text": "GitHub Copilot suggestions are terrible. Waste of money.",
            "expected": "negative",
            "tool": "GitHub Copilot"
        },
        {
            "text": "Midjourney is way too expensive and the results are inconsistent.",
            "expected": "negative",
            "tool": "Midjourney"
        },
        {
            "text": "DeepSeek has too many bugs. Not reliable at all.",
            "expected": "negative",
            "tool": "DeepSeek"
        },

        # Neutral reviews
        {
            "text": "ChatGPT is okay. Works for basic tasks but nothing special.",
            "expected": "neutral",
            "tool": "ChatGPT"
        },
        {
            "text": "Gemini is average compared to other AI assistants. Mixed results.",
            "expected": "neutral",
            "tool": "Gemini"
        },
        {
            "text": "GitHub Copilot has some good suggestions but also many bad ones.",
            "expected": "neutral",
            "tool": "GitHub Copilot"
        },

        # Privacy/security concerns (should detect negative sentiment)
        {
            "text": "ChatGPT has serious privacy issues. They're collecting all my data.",
            "expected": "negative",
            "tool": "ChatGPT"
        },
        {
            "text": "Concerned about data security with Claude. Where is my information stored?",
            "expected": "negative",
            "tool": "Claude"
        },

        # Mixed sentiment
        {
            "text": "ChatGPT is powerful but has some concerning privacy implications.",
            "expected": "neutral",
            "tool": "ChatGPT"
        },
        {
            "text": "GitHub Copilot works well for simple code but struggles with complex logic.",
            "expected": "neutral",
            "tool": "GitHub Copilot"
        },
    ]


def main():
    """Run model tests."""
    print("=" * 70)
    print("AISentinel - Model Testing")
    print("=" * 70)

    # Find latest model
    try:
        model_path = get_latest_model()
        print(f"\nLoading model from: {model_path}")

        tokenizer_path = model_path.parent.parent / "tokenizer.pkl"
        if not tokenizer_path.exists():
            tokenizer_path = model_path.parent / "tokenizer.pkl"

        print(f"Loading tokenizer from: {tokenizer_path}")

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease train a model first:")
        print("  python scripts/train_sentiment_model.py")
        return

    # Initialize analyzer with custom model
    print("\nInitializing analyzer...")
    from src.sentiment_analysis.analyzer import AdvancedSentimentAnalyzer

    analyzer = AdvancedSentimentAnalyzer(
        use_custom_model=True,
        custom_model_path=model_path,
        custom_tokenizer_path=tokenizer_path,
    )

    # Get test reviews
    test_reviews = get_test_reviews()
    print(f"\nTesting on {len(test_reviews)} sample reviews...")
    print("=" * 70)

    # Test each review
    correct = 0
    results = []

    for i, review in enumerate(test_reviews, 1):
        result = analyzer.analyze(review["text"])

        is_correct = result.label == review["expected"]
        if is_correct:
            correct += 1

        results.append({
            "text": review["text"],
            "tool": review["tool"],
            "expected": review["expected"],
            "predicted": result.label,
            "confidence": result.confidence,
            "score": result.score,
            "correct": is_correct,
        })

        # Print result
        status = "✓" if is_correct else "✗"
        print(f"\n{status} Test {i}/{len(test_reviews)}")
        print(f"Tool: {review['tool']}")
        print(f"Text: {review['text'][:70]}...")
        print(f"Expected: {review['expected']:<8} | Predicted: {result.label:<8} | Confidence: {result.confidence:.3f}")

    # Summary
    accuracy = correct / len(test_reviews)
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Total tests: {len(test_reviews)}")
    print(f"Correct:     {correct}")
    print(f"Incorrect:   {len(test_reviews) - correct}")
    print(f"Accuracy:    {accuracy:.1%}")

    # Breakdown by sentiment
    print("\nBreakdown by expected sentiment:")
    for sentiment in ["positive", "negative", "neutral"]:
        subset = [r for r in results if r["expected"] == sentiment]
        if subset:
            subset_correct = sum(1 for r in subset if r["correct"])
            subset_accuracy = subset_correct / len(subset)
            print(f"  {sentiment.capitalize():<8}: {subset_correct}/{len(subset)} ({subset_accuracy:.1%})")

    # Show misclassifications
    misclassified = [r for r in results if not r["correct"]]
    if misclassified:
        print(f"\nMisclassified samples ({len(misclassified)}):")
        for r in misclassified:
            print(f"\n  Text: {r['text'][:60]}...")
            print(f"  Expected: {r['expected']} | Predicted: {r['predicted']} (confidence: {r['confidence']:.3f})")

    print("\n" + "=" * 70)

    # Test with batch processing
    print("\nTesting batch processing...")
    texts = [r["text"] for r in test_reviews[:5]]
    batch_results = analyzer.analyze_batch(texts)
    print(f"✓ Successfully processed batch of {len(texts)} texts")
    print(f"  Results: {[r.label for r in batch_results]}")

    print("\n" + "=" * 70)
    print("Testing complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
