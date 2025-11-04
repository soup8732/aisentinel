from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional

import requests

from . import DataCollector
from src.utils.config import load_config
from src.utils.taxonomy import Category, tools_by_category


@dataclass(frozen=True)
class TweetItem:
    id: str
    author_id: Optional[str]
    created_at: datetime
    text: str
    tool: Optional[str]
    category: Optional[Category]
    like_count: Optional[int]
    retweet_count: Optional[int]
    reply_count: Optional[int]
    quote_count: Optional[int]

    def as_dict(self) -> Mapping[str, Any]:
        return {
            "id": self.id,
            "author_id": self.author_id,
            "created_at": self.created_at.isoformat(),
            "text": self.text,
            "tool": self.tool,
            "category": self.category.value if self.category else None,
            "like_count": self.like_count,
            "retweet_count": self.retweet_count,
            "reply_count": self.reply_count,
            "quote_count": self.quote_count,
        }


class TwitterCollector(DataCollector):
    """Collect tweets by keyword using Twitter API v2 recent search.

    Requires `TWITTER_BEARER_TOKEN` in environment.
    """

    API_URL = "https://api.twitter.com/2/tweets/search/recent"

    def __init__(self, query_terms: Optional[List[str]] = None, limit: int = 100, pause_sec: float = 2.0) -> None:
        self.cfg = load_config()
        self.query_terms = query_terms or self._default_tool_keywords()
        self.limit = limit
        self.pause_sec = pause_sec
        self.token = self.cfg.apis.twitter_bearer_token

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

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def _search(self, query: str, next_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.token:
            return None
        params: Dict[str, Any] = {
            "query": query,
            "max_results": 100,
            "tweet.fields": "created_at,public_metrics,author_id,lang",
        }
        if next_token:
            params["next_token"] = next_token
        try:
            resp = requests.get(self.API_URL, headers=self._headers(), params=params, timeout=20)
            if resp.status_code == 429:
                time.sleep(self.pause_sec)
                return self._search(query, next_token)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def _yield_with_pagination(self, query: str) -> Iterator[Dict[str, Any]]:
        seen = 0
        next_token: Optional[str] = None
        while seen < self.limit:
            payload = self._search(query, next_token)
            if not payload:
                break
            data = payload.get("data", [])
            meta = payload.get("meta", {})
            for item in data:
                yield item
                seen += 1
                if seen >= self.limit:
                    break
            next_token = meta.get("next_token")
            if not next_token:
                break
            time.sleep(self.pause_sec)

    def collect(self) -> Iterable[Mapping[str, Any]]:  # type: ignore[override]
        if not self.token:
            return []
        query = " OR ".join(self.query_terms[:10])
        results: List[Mapping[str, Any]] = []
        for raw in self._yield_with_pagination(query):
            try:
                text = str(raw.get("text", ""))
                created_at = datetime.fromisoformat(str(raw.get("created_at"))).replace(tzinfo=None) if raw.get("created_at") else datetime.utcnow()
                metrics = raw.get("public_metrics", {}) or {}
                tool, category = self._infer_tool_category(text)
                item = TweetItem(
                    id=str(raw.get("id")),
                    author_id=str(raw.get("author_id")) if raw.get("author_id") else None,
                    created_at=created_at,
                    text=text,
                    tool=tool,
                    category=category,
                    like_count=int(metrics.get("like_count", 0)) if isinstance(metrics.get("like_count"), int) else 0,
                    retweet_count=int(metrics.get("retweet_count", 0)) if isinstance(metrics.get("retweet_count"), int) else 0,
                    reply_count=int(metrics.get("reply_count", 0)) if isinstance(metrics.get("reply_count"), int) else 0,
                    quote_count=int(metrics.get("quote_count", 0)) if isinstance(metrics.get("quote_count"), int) else 0,
                )
                results.append(item.as_dict())
            except Exception:
                continue
        return results

