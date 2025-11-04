from __future__ import annotations

from typing import Iterable, Mapping, Any
from .. import DataCollector


class RedditCollector(DataCollector):
    """Collects Reddit posts/comments by keyword (stub).

    Replace with PRAW/Pushshift API calls. This stub yields no data.
    """

    def __init__(self, query: str) -> None:
        self.query = query

    def collect(self) -> Iterable[Mapping[str, Any]]:  # type: ignore[override]
        if not self.query:
            return []
        return []
