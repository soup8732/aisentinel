from __future__ import annotations

from typing import Iterable, Mapping

from src.data_collection.reddit_collector import RedditCollector
from src.data_collection.twitter_collector import TwitterCollector
from src.data_collection.hackernews_collector import HackerNewsCollector


def test_collectors_smoke() -> None:
    reddit = RedditCollector(limit=1, include_comments=False)
    twitter = TwitterCollector(limit=1)
    hn = HackerNewsCollector(limit=1)

    for coll in (reddit, twitter, hn):
        data = coll.collect()
        assert isinstance(data, Iterable)
        # returned items should be mapping-like if any
        for item in list(data)[:1]:
            assert isinstance(item, Mapping)

