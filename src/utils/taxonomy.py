from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Mapping


class Category(str, Enum):
    """High-level AI tool types."""

    TEXT = "text"
    VIDEO_PIC = "video_pic"
    AUDIO = "audio"
    CODE = "code"


class Source(str, Enum):
    """Supported data sources/platforms."""

    TWITTER = "twitter"
    REDDIT = "reddit"
    HN = "hacker_news"
    GITHUB = "github"
    PRODUCT_HUNT = "product_hunt"
    DISCORD = "discord"


@dataclass(frozen=True)
class Tool:
    """Represents a tracked tool and its category."""

    name: str
    category: Category


TOOLS: List[Tool] = [
    # Text & Chat
    Tool("ChatGPT", Category.TEXT),
    Tool("Claude", Category.TEXT),
    Tool("Gemini", Category.TEXT),
    Tool("DeepSeek", Category.TEXT),
    Tool("Mistral", Category.TEXT),
    Tool("Jasper", Category.TEXT),
    Tool("Copy.ai", Category.TEXT),
    Tool("Writesonic", Category.TEXT),
    Tool("Lindy", Category.TEXT),
    # Coding & Dev
    Tool("GitHub Copilot", Category.CODE),
    Tool("Amazon Q Developer", Category.CODE),
    Tool("CodeWhisperer", Category.CODE),
    Tool("Tabnine", Category.CODE),
    Tool("Tabby", Category.CODE),
    Tool("Replit Ghostwriter", Category.CODE),
    Tool("Bolt", Category.CODE),
    Tool("Loveable", Category.CODE),
    Tool("JetBrains AI Assistant", Category.CODE),
    Tool("Cursor", Category.CODE),
    Tool("Codeium", Category.CODE),
    Tool("Polycoder", Category.CODE),
    Tool("AskCodi", Category.CODE),
    Tool("Sourcery", Category.CODE),
    Tool("Greta", Category.CODE),
    # Image & Video
    Tool("Stability AI", Category.VIDEO_PIC),
    Tool("RunwayML", Category.VIDEO_PIC),
    Tool("Midjourney", Category.VIDEO_PIC),
    Tool("DALL-E", Category.VIDEO_PIC),
    Tool("DreamStudio", Category.VIDEO_PIC),
    Tool("OpenCV", Category.VIDEO_PIC),
    Tool("Adobe Firefly", Category.VIDEO_PIC),
    Tool("Pika Labs", Category.VIDEO_PIC),
    Tool("Luma Dream Machine", Category.VIDEO_PIC),
    Tool("Vidu", Category.VIDEO_PIC),
    # Audio & Speech
    Tool("Whisper", Category.AUDIO),
    Tool("ElevenLabs", Category.AUDIO),
    Tool("Murf AI", Category.AUDIO),
    Tool("PlayHT", Category.AUDIO),
    Tool("Speechify", Category.AUDIO),
    Tool("Synthesys", Category.AUDIO),
    Tool("Animaker", Category.AUDIO),
    Tool("Kits AI", Category.AUDIO),
    Tool("WellSaid Labs", Category.AUDIO),
    Tool("Hume", Category.AUDIO),
    Tool("DupDub", Category.AUDIO),
]


def tools_by_category() -> Mapping[Category, List[str]]:
    """Return a mapping from category to list of tool names."""
    by_cat: Dict[Category, List[str]] = {c: [] for c in Category}
    for tool in TOOLS:
        by_cat[tool.category].append(tool.name)
    return by_cat
