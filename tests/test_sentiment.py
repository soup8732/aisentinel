from __future__ import annotations

from dataclasses import dataclass
from src.sentiment_analysis import BaseSentimentAnalyzer, SentimentResult


@dataclass
class DummyAnalyzer(BaseSentimentAnalyzer):
    def analyze(self, text: str) -> SentimentResult:  # type: ignore[override]
        label = "positive" if "good" in text.lower() else "negative"
        score = 0.5 if label == "positive" else -0.5
        return SentimentResult(score=score, label=label)


def test_dummy_analyzer() -> None:
    analyzer = DummyAnalyzer()
    res_pos = analyzer.analyze("This is good")
    res_neg = analyzer.analyze("This is bad")
    assert res_pos.label == "positive" and res_pos.score > 0
    assert res_neg.label == "negative" and res_neg.score < 0
