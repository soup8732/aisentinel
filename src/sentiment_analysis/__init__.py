from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SentimentResult:
    """Container for sentiment analysis output."""

    score: float  # range typically [-1.0, 1.0]
    label: str    # e.g., "positive", "neutral", "negative"


class BaseSentimentAnalyzer(ABC):
    """Base class for sentiment analyzers."""

    @abstractmethod
    def analyze(self, text: str) -> SentimentResult:
        """Analyze a text string and return a sentiment result.

        Args:
            text: Input text to analyze.

        Returns:
            A `SentimentResult` with score and label.
        """
        raise NotImplementedError
