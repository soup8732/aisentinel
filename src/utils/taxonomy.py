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
    # Code
    Tool("VibeCoding", Category.CODE),
    Tool("Tabby", Category.CODE),
    Tool("GitHub Copilot", Category.CODE),
    Tool("CodeWhisperer", Category.CODE),
    Tool("Bolt", Category.CODE),  # builder/agent for code
    Tool("Loveable", Category.CODE),  # lovable.dev code assistant
    # Video/Pic (generative and vision)
    Tool("Stability AI", Category.VIDEO_PIC),
    Tool("RunwayML", Category.VIDEO_PIC),
    Tool("Midjourney", Category.VIDEO_PIC),
    Tool("DALL-E", Category.VIDEO_PIC),
    Tool("DreamStudio", Category.VIDEO_PIC),
    Tool("Segment Anything", Category.VIDEO_PIC),
    Tool("OpenCV", Category.VIDEO_PIC),
    # Text (LLMs/NLP)
    Tool("DeepSeek", Category.TEXT),
    Tool("Llama", Category.TEXT),
    Tool("Hugging Face Transformers", Category.TEXT),
    Tool("GPT-NeoX", Category.TEXT),
    Tool("ChatGPT", Category.TEXT),
    Tool("Claude", Category.TEXT),
    Tool("Gemini", Category.TEXT),
    Tool("Mistral", Category.TEXT),
    Tool("Humain", Category.TEXT),  # general agents/chat
    # Audio (examples)
    Tool("Whisper", Category.AUDIO),
    Tool("ElevenLabs", Category.AUDIO),
]


def tools_by_category() -> Mapping[Category, List[str]]:
    """Return a mapping from category to list of tool names."""
    by_cat: Dict[Category, List[str]] = {c: [] for c in Category}
    for tool in TOOLS:
        by_cat[tool.category].append(tool.name)
    return by_cat
