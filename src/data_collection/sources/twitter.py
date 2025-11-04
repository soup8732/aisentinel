from __future__ import annotations

from typing import Iterable, Mapping, Any
from .. import DataCollector


class TwitterCollector(DataCollector):
    """Collects tweets by keyword/hashtag (stub).

    Replace with Tweepy or Twitter API v2 calls. This stub yields no data.
    """

    def __init__(self, query: str) -> None:
        self.query = query

    def collect(self) -> Iterable[Mapping[str, Any]]:  # type: ignore[override]
        if not self.query:
            return []
        # Return empty for now; implement API calls later
        return []
