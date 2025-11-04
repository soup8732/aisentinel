from __future__ import annotations

from typing import Iterable, Mapping, Any
from .. import DataCollector


class GitHubCollector(DataCollector):
    """Collects GitHub issues/discussions by keyword (stub)."""

    def __init__(self, query: str) -> None:
        self.query = query

    def collect(self) -> Iterable[Mapping[str, Any]]:  # type: ignore[override]
        if not self.query:
            return []
        return []
