"""
Hacker News data collector for AI tool sentiment analysis.

This module collects posts and comments from Hacker News that mention AI tools.
It uses the Algolia HN Search API which requires NO authentication.

This is the easiest collector to use - no API keys needed!

Features:
    - Searches for AI tool mentions in HN posts and comments
    - Automatically infers tool name and category from text
    - Returns normalized data ready for sentiment analysis

Usage:
    from src.data_collection.hackernews_collector import HackerNewsCollector

    # Collect latest mentions
    collector = HackerNewsCollector(limit=100)
    items = list(collector.collect())

    # Save to CSV for sentiment analysis
    import pandas as pd
    df = pd.DataFrame([item.as_dict() for item in items])
    df.to_csv("data/raw/hackernews_data.csv", index=False)

    # Run sentiment analysis on collected data
    from src.sentiment_analysis.analyzer import AdvancedSentimentAnalyzer
    analyzer = AdvancedSentimentAnalyzer()
    results = analyzer.batch_analyze([item.text for item in items])
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional

import requests

from . import DataCollector
from src.utils.taxonomy import Category, tools_by_category


# Algolia HN Search API endpoints (no auth required)
ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
ALGOLIA_SEARCH_BY_DATE_URL = "https://hn.algolia.com/api/v1/search_by_date"


@dataclass(frozen=True)
class HNItem:
    id: str
    created_at: datetime
    title: Optional[str]
    text: str
    url: Optional[str]
    author: Optional[str]
    points: Optional[int]
    num_comments: Optional[int]
    tool: Optional[str]
    category: Optional[Category]

    def as_dict(self) -> Mapping[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "title": self.title,
            "text": self.text,
            "url": self.url,
            "author": self.author,
            "points": self.points,
            "num_comments": self.num_comments,
            "tool": self.tool,
            "category": self.category.value if self.category else None,
        }


class HackerNewsCollector(DataCollector):
    """Collect Hacker News posts/comments mentioning AI tools via Algolia API."""

    def __init__(self, query_terms: Optional[List[str]] = None, limit: int = 100) -> None:
        self.query_terms = query_terms or self._default_tool_keywords()
        self.limit = limit

    def _default_tool_keywords(self) -> List[str]:
        keywords: List[str] = []
        for names in tools_by_category().values():
            keywords.extend(names)
        return sorted({k.lower() for k in keywords})

    def _infer_tool_category(self, text: str) -> tuple[Optional[str], Optional[Category]]:
        t = text.lower()
        for category, names in tools_by_category().items():
            for name in names:
                if name.lower() in t:
                    return name, category
        return None, None

    def _fetch(self, query: str, page: int) -> Optional[Dict[str, Any]]:
        try:
            resp = requests.get(
                ALGOLIA_SEARCH_BY_DATE_URL,
                params={"query": query, "page": page, "hitsPerPage": 50},
                timeout=20,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def collect(self) -> Iterable[Mapping[str, Any]]:  # type: ignore[override]
        results: List[Mapping[str, Any]] = []
        query = " OR ".join(self.query_terms[:10])
        page = 0
        while len(results) < self.limit:
            payload = self._fetch(query, page)
            if not payload:
                break
            hits = payload.get("hits", [])
            if not hits:
                break
            for hit in hits:
                try:
                    text = (hit.get("title") or "") + "\n\n" + (hit.get("comment_text") or hit.get("story_text") or "")
                    text = text.strip()
                    tool, category = self._infer_tool_category(text)
                    dt = hit.get("created_at")
                    created_at = datetime.fromisoformat(dt.replace("Z", "+00:00")).replace(tzinfo=None) if isinstance(dt, str) else datetime.utcnow()
                    item = HNItem(
                        id=str(hit.get("objectID")),
                        created_at=created_at,
                        title=hit.get("title") or hit.get("story_title"),
                        text=text,
                        url=hit.get("url") or hit.get("story_url"),
                        author=hit.get("author"),
                        points=hit.get("points"),
                        num_comments=hit.get("num_comments"),
                        tool=tool,
                        category=category,
                    )
                    results.append(item.as_dict())
                    if len(results) >= self.limit:
                        break
                except Exception:
                    continue
            page += 1
        return results

