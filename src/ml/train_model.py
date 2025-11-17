"""Train custom TensorFlow sentiment analysis model.

This script:
1. Loads preprocessed training data
2. Builds and trains a custom TensorFlow model
3. Evaluates on validation and test sets
4. Saves the trained model and tokenizer
5. Generates evaluation metrics and visualizations
"""
from __future__ import annotations

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
    precision_recall_curve,
)

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau,
    TensorBoard,
)

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.ml.model import build_sentiment_model, build_transformer_based_model


class SentimentModelTrainer:
    """Handles training and evaluation of sentiment models."""

    def __init__(
        self,
        data_dir: Path,
        output_dir: Path,
        max_vocab_size: int = 10000,
        max_length: int = 128,
        model_type: str = "lstm",  # "lstm" or "transformer"
    ):
        """Initialize trainer.

        Args:
            data_dir: Directory containing train/val/test CSVs
            output_dir: Directory to save models and results
            max_vocab_size: Maximum vocabulary size
            max_length: Maximum sequence length
            model_type: Type of model architecture
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.max_vocab_size = max_vocab_size
        self.max_length = max_length
        self.model_type = model_type

        self.tokenizer = None
        self.model = None
        self.history = None

        # Label mapping
        self.label_map = {"negative": 0, "neutral": 1, "positive": 2}
        self.reverse_label_map = {v: k for k, v in self.label_map.items()}

    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load train, validation, and test datasets."""
        train_df = pd.read_csv(self.data_dir / "train.csv")
        val_df = pd.read_csv(self.data_dir / "val.csv")
        test_df = pd.read_csv(self.data_dir / "test.csv")

        print(f"Loaded {len(train_df)} training samples")
        print(f"Loaded {len(val_df)} validation samples")
        print(f"Loaded {len(test_df)} test samples")

        return train_df, val_df, test_df

    def prepare_tokenizer(self, train_df: pd.DataFrame) -> Tokenizer:
        """Build and fit tokenizer on training data."""
        print("\nBuilding tokenizer...")
        tokenizer = Tokenizer(
            num_words=self.max_vocab_size,
            oov_token="<OOV>",
            lower=True,
        )
        tokenizer.fit_on_texts(train_df["text"].tolist())

        vocab_size = len(tokenizer.word_index) + 1
        print(f"Vocabulary size: {vocab_size}")

        # Save tokenizer
        tokenizer_path = self.output_dir / "tokenizer.pkl"
        with open(tokenizer_path, "wb") as f:
            pickle.dump(tokenizer, f)
        print(f"Tokenizer saved to {tokenizer_path}")

        self.tokenizer = tokenizer
        return tokenizer

    def prepare_sequences(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convert texts to padded sequences."""
        sequences = self.tokenizer.texts_to_sequences(df["text"].tolist())
        padded = pad_sequences(
            sequences,
            maxlen=self.max_length,
            padding="post",
            truncating="post",
        )
        labels = df["label"].values
        return padded, labels

    def build_model(self) -> keras.Model:
        """Build model based on selected architecture."""
        vocab_size = min(self.max_vocab_size, len(self.tokenizer.word_index) + 1)

        print(f"\nBuilding {self.model_type} model...")

        if self.model_type == "lstm":
            model = build_sentiment_model(
                vocab_size=vocab_size,
                embedding_dim=128,
                max_length=self.max_length,
                num_classes=3,
                lstm_units=64,
                dropout_rate=0.5,
                use_attention=True,
            )
        elif self.model_type == "transformer":
            model = build_transformer_based_model(
                vocab_size=vocab_size,
                embedding_dim=128,
                max_length=self.max_length,
                num_classes=3,
                num_heads=4,
                ff_dim=128,
                dropout_rate=0.3,
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

        self.model = model
        return model

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        epochs: int = 20,
        batch_size: int = 32,
    ) -> keras.callbacks.History:
        """Train the model with callbacks."""
        print("\nStarting training...")

        # Create checkpoint directory
        checkpoint_dir = self.output_dir / "checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)

        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor="val_loss",
                patience=5,
                restore_best_weights=True,
                verbose=1,
            ),
            ModelCheckpoint(
                filepath=str(checkpoint_dir / "best_model.keras"),
                monitor="val_accuracy",
                save_best_only=True,
                verbose=1,
            ),
            ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.5,
                patience=3,
                min_lr=1e-7,
                verbose=1,
            ),
            TensorBoard(
                log_dir=str(self.output_dir / "logs"),
                histogram_freq=1,
            ),
        ]

        # Train
        history = self.model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1,
        )

        self.history = history
        return history

    def evaluate(
        self, X_test: np.ndarray, y_test: np.ndarray
    ) -> dict:
        """Evaluate model and generate metrics."""
        print("\nEvaluating model on test set...")

        # Predictions
        y_pred_probs = self.model.predict(X_test, verbose=0)
        y_pred = np.argmax(y_pred_probs, axis=1)

        # Classification report
        report = classification_report(
            y_test,
            y_pred,
            target_names=list(self.reverse_label_map.values()),
            output_dict=True,
        )

        print("\nClassification Report:")
        print(classification_report(
            y_test,
            y_pred,
            target_names=list(self.reverse_label_map.values()),
        ))

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)

        # Save metrics
        metrics = {
            "test_accuracy": float(report["accuracy"]),
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "model_type": self.model_type,
            "vocab_size": len(self.tokenizer.word_index),
            "max_length": self.max_length,
            "timestamp": datetime.now().isoformat(),
        }

        metrics_path = self.output_dir / "metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"\nMetrics saved to {metrics_path}")

        return metrics

    def plot_training_history(self):
        """Plot training history."""
        if self.history is None:
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Accuracy
        axes[0, 0].plot(self.history.history["accuracy"], label="Train")
        axes[0, 0].plot(self.history.history["val_accuracy"], label="Val")
        axes[0, 0].set_title("Model Accuracy")
        axes[0, 0].set_xlabel("Epoch")
        axes[0, 0].set_ylabel("Accuracy")
        axes[0, 0].legend()
        axes[0, 0].grid(True)

        # Loss
        axes[0, 1].plot(self.history.history["loss"], label="Train")
        axes[0, 1].plot(self.history.history["val_loss"], label="Val")
        axes[0, 1].set_title("Model Loss")
        axes[0, 1].set_xlabel("Epoch")
        axes[0, 1].set_ylabel("Loss")
        axes[0, 1].legend()
        axes[0, 1].grid(True)

        # Precision
        if "precision" in self.history.history:
            axes[1, 0].plot(self.history.history["precision"], label="Train")
            axes[1, 0].plot(self.history.history["val_precision"], label="Val")
            axes[1, 0].set_title("Model Precision")
            axes[1, 0].set_xlabel("Epoch")
            axes[1, 0].set_ylabel("Precision")
            axes[1, 0].legend()
            axes[1, 0].grid(True)

        # Recall
        if "recall" in self.history.history:
            axes[1, 1].plot(self.history.history["recall"], label="Train")
            axes[1, 1].plot(self.history.history["val_recall"], label="Val")
            axes[1, 1].set_title("Model Recall")
            axes[1, 1].set_xlabel("Epoch")
            axes[1, 1].set_ylabel("Recall")
            axes[1, 1].legend()
            axes[1, 1].grid(True)

        plt.tight_layout()
        plt.savefig(self.output_dir / "training_history.png", dpi=150)
        print(f"Training history plot saved to {self.output_dir / 'training_history.png'}")
        plt.close()

    def plot_confusion_matrix(self, y_test: np.ndarray):
        """Plot confusion matrix."""
        y_pred = np.argmax(self.model.predict(y_test, verbose=0), axis=1)
        cm = confusion_matrix(y_test, y_pred)

        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=list(self.reverse_label_map.values()),
            yticklabels=list(self.reverse_label_map.values()),
        )
        plt.title("Confusion Matrix")
        plt.ylabel("True Label")
        plt.xlabel("Predicted Label")
        plt.tight_layout()
        plt.savefig(self.output_dir / "confusion_matrix.png", dpi=150)
        print(f"Confusion matrix saved to {self.output_dir / 'confusion_matrix.png'}")
        plt.close()

    def save_model(self):
        """Save the final model."""
        model_path = self.output_dir / "sentiment_model.keras"
        self.model.save(model_path)
        print(f"\nModel saved to {model_path}")

        # Also save in SavedModel format for deployment
        saved_model_path = self.output_dir / "saved_model"
        self.model.export(saved_model_path)
        print(f"SavedModel exported to {saved_model_path}")


def main():
    """Main training pipeline."""
    print("=" * 70)
    print("AISentinel - Sentiment Model Training")
    print("=" * 70)

    # Paths
    data_dir = PROJECT_ROOT / "data" / "processed"
    output_dir = PROJECT_ROOT / "models" / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Configuration
    config = {
        "max_vocab_size": 10000,
        "max_length": 128,
        "model_type": "lstm",  # or "transformer"
        "epochs": 20,
        "batch_size": 32,
    }

    print(f"\nConfiguration:")
    for key, value in config.items():
        print(f"  {key}: {value}")

    # Initialize trainer
    trainer = SentimentModelTrainer(
        data_dir=data_dir,
        output_dir=output_dir,
        max_vocab_size=config["max_vocab_size"],
        max_length=config["max_length"],
        model_type=config["model_type"],
    )

    # Load data
    train_df, val_df, test_df = trainer.load_data()

    # Prepare tokenizer
    tokenizer = trainer.prepare_tokenizer(train_df)

    # Prepare sequences
    X_train, y_train = trainer.prepare_sequences(train_df)
    X_val, y_val = trainer.prepare_sequences(val_df)
    X_test, y_test = trainer.prepare_sequences(test_df)

    print(f"\nTraining data shape: {X_train.shape}")
    print(f"Validation data shape: {X_val.shape}")
    print(f"Test data shape: {X_test.shape}")

    # Build model
    model = trainer.build_model()
    model.summary()

    # Train
    history = trainer.train(
        X_train, y_train,
        X_val, y_val,
        epochs=config["epochs"],
        batch_size=config["batch_size"],
    )

    # Evaluate
    metrics = trainer.evaluate(X_test, y_test)

    # Visualizations
    trainer.plot_training_history()
    trainer.plot_confusion_matrix(X_test)

    # Save model
    trainer.save_model()

    # Save configuration
    config_path = output_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print("\n" + "=" * 70)
    print("Training Complete!")
    print("=" * 70)
    print(f"\nResults saved to: {output_dir}")
    print(f"Test Accuracy: {metrics['test_accuracy']:.4f}")
    print("\nNext steps:")
    print("  1. Review metrics and visualizations")
    print("  2. Update AdvancedSentimentAnalyzer to use this model")
    print("  3. Test with real AI tool reviews")


if __name__ == "__main__":
    main()
