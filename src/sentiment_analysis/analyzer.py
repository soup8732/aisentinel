from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, List, Optional, Sequence

import math

try:
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover
    pipeline = None  # type: ignore

try:
    import tensorflow as tf  # type: ignore
except Exception:  # pragma: no cover
    tf = None  # type: ignore

from . import BaseSentimentAnalyzer, SentimentResult


@dataclass(frozen=True)
class AdvancedSentimentResult(SentimentResult):
    """Sentiment result including a confidence score in [0,1]."""

    confidence: float = 0.0


class AdvancedSentimentAnalyzer(BaseSentimentAnalyzer):
    """Advanced analyzer combining transformers and TensorFlow paths.

    - Uses transformers pipeline as the primary model.
    - Optionally validates/refines via a lightweight TF head if available.
    - Supports batch processing and model caching.
    - Returns confidence scores derived from model probabilities.
    """

    def __init__(self, transformer_model: Optional[str] = None, batch_size: int = 16) -> None:
        self.transformer_model = transformer_model or "distilbert-base-uncased-finetuned-sst-2-english"
        self.batch_size = max(1, batch_size)
        self._pipe = self._get_transformer_pipeline()
        self._tf_head = self._get_tf_head()

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

    def analyze(self, text: str) -> AdvancedSentimentResult:  # type: ignore[override]
        if not text.strip() or self._pipe is None:
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

