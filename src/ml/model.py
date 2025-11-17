"""Custom TensorFlow sentiment analysis model.

Implements a hybrid architecture combining:
- Pre-trained embeddings (GloVe or word2vec)
- Bidirectional LSTM layers for sequence modeling
- Attention mechanism for focusing on important words
- Dense layers for classification

This showcases advanced deep learning techniques for NLP.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


class AttentionLayer(layers.Layer):
    """Custom attention layer to focus on important words in the sequence."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self, input_shape):
        # attention weights
        self.W = self.add_weight(
            name="attention_weight",
            shape=(input_shape[-1], input_shape[-1]),
            initializer="glorot_uniform",
            trainable=True,
        )
        self.b = self.add_weight(
            name="attention_bias",
            shape=(input_shape[-1],),
            initializer="zeros",
            trainable=True,
        )
        super().build(input_shape)

    def call(self, inputs):
        # inputs shape: (batch_size, time_steps, features)
        # Score calculation
        score = tf.nn.tanh(tf.tensordot(inputs, self.W, axes=1) + self.b)
        # Attention weights
        attention_weights = tf.nn.softmax(score, axis=1)
        # Context vector
        context_vector = attention_weights * inputs
        context_vector = tf.reduce_sum(context_vector, axis=1)
        return context_vector

    def get_config(self):
        return super().get_config()


def build_sentiment_model(
    vocab_size: int,
    embedding_dim: int = 128,
    max_length: int = 128,
    num_classes: int = 3,
    lstm_units: int = 64,
    dropout_rate: float = 0.5,
    use_attention: bool = True,
) -> keras.Model:
    """Build custom sentiment analysis model with TensorFlow/Keras.

    Architecture:
    1. Embedding layer (trainable or pre-trained)
    2. Spatial Dropout for regularization
    3. Bidirectional LSTM layers
    4. Optional Attention mechanism
    5. Dense layers with dropout
    6. Softmax output for multi-class classification

    Args:
        vocab_size: Size of vocabulary
        embedding_dim: Dimension of word embeddings
        max_length: Maximum sequence length
        num_classes: Number of sentiment classes (3: neg/neu/pos)
        lstm_units: Number of LSTM units per direction
        dropout_rate: Dropout rate for regularization
        use_attention: Whether to use attention mechanism

    Returns:
        Compiled Keras model
    """
    # Input layer
    inputs = layers.Input(shape=(max_length,), dtype=tf.int32, name="input_ids")

    # Embedding layer
    x = layers.Embedding(
        input_dim=vocab_size,
        output_dim=embedding_dim,
        input_length=max_length,
        mask_zero=True,
        name="embedding",
    )(inputs)

    # Spatial dropout for embeddings
    x = layers.SpatialDropout1D(dropout_rate * 0.5)(x)

    # First Bidirectional LSTM
    x = layers.Bidirectional(
        layers.LSTM(
            lstm_units,
            return_sequences=True,
            dropout=dropout_rate * 0.3,
            recurrent_dropout=dropout_rate * 0.3,
        ),
        name="bi_lstm_1",
    )(x)

    # Second Bidirectional LSTM
    x = layers.Bidirectional(
        layers.LSTM(
            lstm_units // 2,
            return_sequences=use_attention,
            dropout=dropout_rate * 0.3,
            recurrent_dropout=dropout_rate * 0.3,
        ),
        name="bi_lstm_2",
    )(x)

    # Attention mechanism (optional)
    if use_attention:
        x = AttentionLayer(name="attention")(x)

    # Dense layers
    x = layers.Dense(64, activation="relu", name="dense_1")(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Dense(32, activation="relu", name="dense_2")(x)
    x = layers.Dropout(dropout_rate * 0.5)(x)

    # Output layer
    outputs = layers.Dense(num_classes, activation="softmax", name="output")(x)

    # Build model
    model = keras.Model(inputs=inputs, outputs=outputs, name="sentiment_model")

    # Compile with optimizer and loss
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=[
            "accuracy",
            keras.metrics.SparseCategoricalAccuracy(name="sparse_categorical_accuracy"),
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
        ],
    )

    return model


def build_transformer_based_model(
    vocab_size: int,
    embedding_dim: int = 128,
    max_length: int = 128,
    num_classes: int = 3,
    num_heads: int = 4,
    ff_dim: int = 128,
    dropout_rate: float = 0.3,
) -> keras.Model:
    """Build transformer-based sentiment model (more advanced).

    Uses multi-head self-attention instead of LSTM.

    Args:
        vocab_size: Size of vocabulary
        embedding_dim: Dimension of embeddings
        max_length: Maximum sequence length
        num_classes: Number of output classes
        num_heads: Number of attention heads
        ff_dim: Feed-forward network dimension
        dropout_rate: Dropout rate

    Returns:
        Compiled Keras model
    """
    # Input
    inputs = layers.Input(shape=(max_length,), dtype=tf.int32)

    # Embedding + Positional encoding
    embedding_layer = layers.Embedding(vocab_size, embedding_dim)
    x = embedding_layer(inputs)

    # Add positional encoding
    positions = tf.range(start=0, limit=max_length, delta=1)
    position_embedding = layers.Embedding(max_length, embedding_dim)(positions)
    x = x + position_embedding

    # Multi-head self-attention
    attention_output = layers.MultiHeadAttention(
        num_heads=num_heads,
        key_dim=embedding_dim // num_heads,
        dropout=dropout_rate,
    )(x, x)

    # Skip connection + LayerNorm
    x = layers.Add()([x, attention_output])
    x = layers.LayerNormalization(epsilon=1e-6)(x)

    # Feed-forward network
    ffn = keras.Sequential([
        layers.Dense(ff_dim, activation="relu"),
        layers.Dropout(dropout_rate),
        layers.Dense(embedding_dim),
    ])
    ffn_output = ffn(x)

    # Skip connection + LayerNorm
    x = layers.Add()([x, ffn_output])
    x = layers.LayerNormalization(epsilon=1e-6)(x)

    # Global pooling
    x = layers.GlobalAveragePooling1D()(x)

    # Classification head
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(dropout_rate)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs=inputs, outputs=outputs)

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy", keras.metrics.Precision(), keras.metrics.Recall()],
    )

    return model


class SentimentModelWrapper:
    """Wrapper for trained sentiment model with preprocessing."""

    def __init__(self, model_path: Path, tokenizer_path: Path):
        """Load saved model and tokenizer.

        Args:
            model_path: Path to saved Keras model
            tokenizer_path: Path to saved tokenizer
        """
        self.model = keras.models.load_model(
            model_path,
            custom_objects={"AttentionLayer": AttentionLayer},
        )

        import pickle
        with open(tokenizer_path, "rb") as f:
            self.tokenizer = pickle.load(f)

        self.label_map = {0: "negative", 1: "neutral", 2: "positive"}

    def predict(self, texts: list[str]) -> list[dict]:
        """Predict sentiment for a list of texts.

        Args:
            texts: List of text strings

        Returns:
            List of dictionaries with predictions
        """
        # Tokenize and pad
        sequences = self.tokenizer.texts_to_sequences(texts)
        padded = keras.preprocessing.sequence.pad_sequences(
            sequences,
            maxlen=self.model.input_shape[1],
            padding="post",
            truncating="post",
        )

        # Predict
        predictions = self.model.predict(padded, verbose=0)

        # Format results
        results = []
        for i, pred in enumerate(predictions):
            label_idx = int(np.argmax(pred))
            confidence = float(pred[label_idx])
            results.append({
                "text": texts[i],
                "label": self.label_map[label_idx],
                "confidence": confidence,
                "probabilities": {
                    "negative": float(pred[0]),
                    "neutral": float(pred[1]),
                    "positive": float(pred[2]),
                },
            })

        return results


if __name__ == "__main__":
    # Example: Build and display model architecture
    print("Building LSTM-based sentiment model...")
    lstm_model = build_sentiment_model(
        vocab_size=10000,
        embedding_dim=128,
        max_length=128,
        num_classes=3,
        use_attention=True,
    )
    lstm_model.summary()

    print("\n" + "=" * 60)
    print("Building Transformer-based sentiment model...")
    transformer_model = build_transformer_based_model(
        vocab_size=10000,
        embedding_dim=128,
        max_length=128,
        num_classes=3,
    )
    transformer_model.summary()
