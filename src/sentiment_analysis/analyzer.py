from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional, Sequence
import pickle

import math
import numpy as np

try:
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover
    pipeline = None  # type: ignore

try:
    import tensorflow as tf  # type: ignore
    from tensorflow import keras
except Exception:  # pragma: no cover
    tf = None  # type: ignore
    keras = None  # type: ignore

from . import BaseSentimentAnalyzer, SentimentResult


@dataclass(frozen=True)
class AdvancedSentimentResult(SentimentResult):
    """Sentiment result including a confidence score in [0,1]."""

    confidence: float = 0.0


class AdvancedSentimentAnalyzer(BaseSentimentAnalyzer):
    """Advanced analyzer combining transformers and custom TensorFlow models.

    Can operate in three modes:
    1. Custom TF model only (use_custom_model=True, custom_model_path provided)
    2. Transformers + TF refinement (use_custom_model=True, no custom_model_path)
    3. Transformers only (use_custom_model=False)

    - Supports custom trained TensorFlow models for domain-specific sentiment
    - Falls back to transformers pipeline if custom model unavailable
    - Supports batch processing and model caching
    - Returns confidence scores derived from model probabilities
    """

    def __init__(
        self,
        transformer_model: Optional[str] = None,
        batch_size: int = 16,
        use_custom_model: bool = True,
        custom_model_path: Optional[Path] = None,
        custom_tokenizer_path: Optional[Path] = None,
    ) -> None:
        self.transformer_model = transformer_model or "distilbert-base-uncased-finetuned-sst-2-english"
        self.batch_size = max(1, batch_size)
        self.use_custom_model = use_custom_model

        # Try to load custom model if requested
        self._custom_model = None
        self._custom_tokenizer = None
        self._max_length = 128

        if use_custom_model and custom_model_path:
            self._load_custom_model(custom_model_path, custom_tokenizer_path)

        # Fall back to transformers if custom model not available
        if self._custom_model is None:
            self._pipe = self._get_transformer_pipeline()
            self._tf_head = self._get_tf_head()
        else:
            self._pipe = None
            self._tf_head = None

        self.label_map = {0: "negative", 1: "neutral", 2: "positive"}

    def _load_custom_model(
        self, model_path: Path, tokenizer_path: Optional[Path] = None
    ) -> None:
        """Load custom TensorFlow model and tokenizer."""
        try:
            if keras is None:
                return

            # Load custom attention layer if needed
            try:
                from src.ml.model import AttentionLayer
                custom_objects = {"AttentionLayer": AttentionLayer}
            except Exception:
                custom_objects = {}

            # Load model
            self._custom_model = keras.models.load_model(
                str(model_path), custom_objects=custom_objects
            )

            # Load tokenizer
            if tokenizer_path and tokenizer_path.exists():
                with open(tokenizer_path, "rb") as f:
                    self._custom_tokenizer = pickle.load(f)

                # Get max length from model input shape
                if self._custom_model is not None:
                    self._max_length = self._custom_model.input_shape[1]

        except Exception as e:
            print(f"Warning: Could not load custom model: {e}")
            self._custom_model = None
            self._custom_tokenizer = None

    @lru_cache(maxsize=1)
    def _get_transformer_pipeline(self):  # type: ignore[no-untyped-def]
        if pipeline is None:
            return None
        return pipeline("sentiment-analysis", model=self.transformer_model)

    @lru_cache(maxsize=1)
    def _get_tf_head(self):  # type: ignore[no-untyped-def]
        if tf is None:
            return None
        # A tiny dense layer as a placeholder; in real use, load a saved model
        inputs = tf.keras.Input(shape=(1,), dtype=tf.float32)
        x = tf.keras.layers.Dense(2, activation="softmax")(inputs)
        model = tf.keras.Model(inputs, x)
        return model

    def _postprocess(self, label: str, score: float) -> AdvancedSentimentResult:
        lbl = label.lower()
        if lbl.startswith("neg"):
            return AdvancedSentimentResult(score=-abs(score), label="negative", confidence=float(abs(score)))
        if lbl.startswith("pos"):
            return AdvancedSentimentResult(score=abs(score), label="positive", confidence=float(abs(score)))
        return AdvancedSentimentResult(score=0.0, label="neutral", confidence=0.5)

    def _predict_with_custom_model(self, texts: List[str]) -> List[AdvancedSentimentResult]:
        """Predict using custom TensorFlow model."""
        if self._custom_model is None or self._custom_tokenizer is None:
            return [AdvancedSentimentResult(score=0.0, label="neutral", confidence=0.0) for _ in texts]

        try:
            # Tokenize and pad
            sequences = self._custom_tokenizer.texts_to_sequences(texts)
            padded = keras.preprocessing.sequence.pad_sequences(
                sequences, maxlen=self._max_length, padding="post", truncating="post"
            )

            # Predict
            predictions = self._custom_model.predict(padded, verbose=0)

            # Convert to results
            results = []
            for pred in predictions:
                label_idx = int(np.argmax(pred))
                confidence = float(pred[label_idx])
                label = self.label_map.get(label_idx, "neutral")

                # Convert to score in [-1, 1] range
                if label == "negative":
                    score = -confidence
                elif label == "positive":
                    score = confidence
                else:
                    score = 0.0

                results.append(
                    AdvancedSentimentResult(
                        score=score, label=label, confidence=confidence
                    )
                )

            return results
        except Exception:
            return [AdvancedSentimentResult(score=0.0, label="neutral", confidence=0.0) for _ in texts]

    def analyze(self, text: str) -> AdvancedSentimentResult:  # type: ignore[override]
        if not text.strip():
            return AdvancedSentimentResult(score=0.0, label="neutral", confidence=0.0)

        # Use custom model if available
        if self._custom_model is not None:
            return self._predict_with_custom_model([text])[0]

        # Fall back to transformers
        if self._pipe is None:
            return AdvancedSentimentResult(score=0.0, label="neutral", confidence=0.0)

        raw = self._pipe(text)[0]
        result = self._postprocess(str(raw.get("label", "neutral")), float(raw.get("score", 0.0)))

        # Optionally adjust with TF head (toy logic)
        if self._tf_head is not None:
            adjust = float(self._tf_head.predict([[abs(result.score)]], verbose=0)[0][0])  # type: ignore[index]
            # Blend confidence
            result = AdvancedSentimentResult(score=result.score, label=result.label, confidence=float(min(1.0, (result.confidence + adjust) / 2.0)))
        return result

    def analyze_batch(self, texts: Sequence[str]) -> List[AdvancedSentimentResult]:
        # Use custom model if available
        if self._custom_model is not None:
            return self._predict_with_custom_model(list(texts))

        # Fall back to transformers
        if self._pipe is None:
            return [AdvancedSentimentResult(score=0.0, label="neutral", confidence=0.0) for _ in texts]

        outputs: List[AdvancedSentimentResult] = []
        for i in range(0, len(texts), self.batch_size):
            chunk = texts[i : i + self.batch_size]
            raw_batch = self._pipe(list(chunk))
            for raw in raw_batch:
                result = self._postprocess(str(raw.get("label", "neutral")), float(raw.get("score", 0.0)))
                outputs.append(result)
        return outputs

