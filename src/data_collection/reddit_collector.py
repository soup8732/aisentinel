"""
Reddit data collector for AI tool sentiment analysis.

This module collects posts and comments from Reddit that mention AI tools.
It searches specified subreddits (default: MachineLearning, AI, OpenAI, DataScience)
and extracts text data for sentiment analysis.

Requirements:
    - PRAW library (pip install praw)
    - Reddit API credentials in .env file:
        REDDIT_CLIENT_ID=your_client_id
        REDDIT_CLIENT_SECRET=your_client_secret
        REDDIT_USER_AGENT=aisentinel/0.1.0

Setup: See docs/API_SETUP.md for detailed instructions.

Usage:
    from src.data_collection.reddit_collector import RedditCollector

    collector = RedditCollector(limit=100)
    items = list(collector.collect())

    # Save to CSV
    import pandas as pd
    df = pd.DataFrame([item.as_dict() for item in items])
    df.to_csv("data/raw/reddit_data.csv", index=False)
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from time import sleep
from typing import Iterable, Iterator, List, Mapping, Optional, Any

try:
    import praw  # type: ignore
    from praw.models import Submission, Comment  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    praw = None  # type: ignore
    Submission = object  # type: ignore
    Comment = object  # type: ignore

from . import DataCollector
from src.utils.config import load_config
from src.utils.taxonomy import Category, tools_by_category


@dataclass(frozen=True)
class RedditItem:
    """Normalized Reddit item."""

    id: str
    type: str  # "post" or "comment"
    subreddit: str
    author: Optional[str]
    created_utc: float
    created_at: datetime
    title: Optional[str]
    text: str
    url: Optional[str]
    score: Optional[int]
    num_comments: Optional[int]
    tool: Optional[str]
    category: Optional[Category]

    def as_dict(self) -> Mapping[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "subreddit": self.subreddit,
            "author": self.author,
            "created_utc": self.created_utc,
            "created_at": self.created_at.isoformat(),
            "title": self.title,
            "text": self.text,
            "url": self.url,
            "score": self.score,
            "num_comments": self.num_comments,
            "tool": self.tool,
            "category": self.category.value if self.category else None,
        }


class RedditCollector(DataCollector):
    """Collect Reddit posts and comments for AI tools from specified subreddits.

    Requires PRAW and Reddit API credentials in environment/config.
    """

    def __init__(
        self,
        subreddits: Optional[List[str]] = None,
        query_terms: Optional[List[str]] = None,
        limit: int = 100,
        include_comments: bool = True,
        sleep_sec_on_rate_limit: float = 2.0,
    ) -> None:
        self.cfg = load_config()
        self.subreddits = subreddits or ["MachineLearning", "ArtificialInteligence", "OpenAI", "DataScience"]
        self.query_terms = query_terms or self._default_tool_keywords()
        self.limit = limit
        self.include_comments = include_comments
        self.sleep_sec_on_rate_limit = sleep_sec_on_rate_limit
        self._reddit = self._init_client()

    def _init_client(self):  # type: ignore[no-untyped-def]
        if not praw:
            return None
        creds = self.cfg.apis
        if not (creds.reddit_client_id and creds.reddit_client_secret and creds.reddit_user_agent):
            return None
        return praw.Reddit(
            client_id=creds.reddit_client_id,
            client_secret=creds.reddit_client_secret,
            user_agent=creds.reddit_user_agent,
        )

    def _default_tool_keywords(self) -> List[str]:
        keywords: List[str] = []
        for names in tools_by_category().values():
            keywords.extend(names)
        # ensure lowercase unique tokens
        return sorted({k.lower() for k in keywords})

    def _matches_query(self, text: str) -> bool:
        t = text.lower()
        return any(term in t for term in self.query_terms)

    def _normalize_submission(self, s: Submission) -> Optional[RedditItem]:  # type: ignore[name-defined]
        try:
            title = getattr(s, "title", None) or ""
            body = getattr(s, "selftext", "") or ""
            full_text = f"{title}\n\n{body}".strip()
            if not self._matches_query(full_text):
                return None
            created_utc = float(getattr(s, "created_utc", 0.0))
            created_at = datetime.utcfromtimestamp(created_utc)
            tool, category = self._infer_tool_category(full_text)
            return RedditItem(
                id=str(getattr(s, "id", "")),
                type="post",
                subreddit=str(getattr(s, "subreddit", "")),
                author=str(getattr(s, "author", None)) if getattr(s, "author", None) else None,
                created_utc=created_utc,
                created_at=created_at,
                title=title or None,
                text=full_text,
                url=str(getattr(s, "url", None)) if getattr(s, "url", None) else None,
                score=int(getattr(s, "score", 0)) if hasattr(s, "score") else None,
                num_comments=int(getattr(s, "num_comments", 0)) if hasattr(s, "num_comments") else None,
                tool=tool,
                category=category,
            )
        except Exception:
            return None

    def _normalize_comment(self, c: Comment) -> Optional[RedditItem]:  # type: ignore[name-defined]
        try:
            body = str(getattr(c, "body", ""))
            if not self._matches_query(body):
                return None
            created_utc = float(getattr(c, "created_utc", 0.0))
            created_at = datetime.utcfromtimestamp(created_utc)
            tool, category = self._infer_tool_category(body)
            return RedditItem(
                id=str(getattr(c, "id", "")),
                type="comment",
                subreddit=str(getattr(c, "subreddit", "")),
                author=str(getattr(c, "author", None)) if getattr(c, "author", None) else None,
                created_utc=created_utc,
                created_at=created_at,
                title=None,
                text=body,
                url=None,
                score=int(getattr(c, "score", 0)) if hasattr(c, "score") else None,
                num_comments=None,
                tool=tool,
                category=category,
            )
        except Exception:
            return None

    def _infer_tool_category(self, text: str) -> tuple[Optional[str], Optional[Category]]:
        t = text.lower()
        for category, names in tools_by_category().items():
            for name in names:
                if name.lower() in t:
                    return name, category
        return None, None

    def _yield_with_rate_limit(self, items: Iterable) -> Iterator:  # type: ignore[no-untyped-def]
        for item in items:
            yield item
            sleep(self.sleep_sec_on_rate_limit)

    def collect(self) -> Iterable[Mapping[str, Any]]:  # type: ignore[override]
        if not self._reddit:
            return []
        results: List[Mapping[str, Any]] = []
        try:
            for sub in self.subreddits:
                subreddit = self._reddit.subreddit(sub)
                # Search recent posts matching any keyword
                query = " OR ".join(self.query_terms[:10])  # limit length for API sanity
                submissions = subreddit.search(query=query, sort="new", limit=self.limit)
                for s in self._yield_with_rate_limit(submissions):
                    item = self._normalize_submission(s)
                    if item:
                        results.append(item.as_dict())
                        if self.include_comments:
                            s.comments.replace_more(limit=0)
                            for c in s.comments.list():
                                c_item = self._normalize_comment(c)
                                if c_item:
                                    results.append(c_item.as_dict())
        except Exception:
            # Swallow and return what we have; production code should log
            return results
        return results

