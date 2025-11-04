from __future__ import annotations

from typing import Optional

try:
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover - allow runtime without transformers installed
    pipeline = None  # type: ignore

from .. import BaseSentimentAnalyzer, SentimentResult


class TransformersSentimentAnalyzer(BaseSentimentAnalyzer):
    """Wrapper around a transformers pipeline for sentiment analysis.

    If `transformers` is not installed, falls back to a neutral response.
    """

    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model or "distilbert-base-uncased-finetuned-sst-2-english"
        self._pipe = pipeline("sentiment-analysis", model=self.model) if pipeline else None

    def analyze(self, text: str) -> SentimentResult:  # type: ignore[override]
        if not self._pipe:
            return SentimentResult(score=0.0, label="neutral")
        result = self._pipe(text)[0]
        label = str(result.get("label", "NEUTRAL")).lower()
        score = float(result.get("score", 0.0))
        if label.startswith("neg"):
            score = -abs(score)
            label = "negative"
        elif label.startswith("pos"):
            score = abs(score)
            label = "positive"
        else:
            score = 0.0
            label = "neutral"
        return SentimentResult(score=score, label=label)
