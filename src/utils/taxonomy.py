from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Mapping


class Category(str, Enum):
    """High-level AI tool categories."""

    CODING = "coding_assistants"
    GENERATIVE = "generative_image_video"
    NLP = "nlp_llms"
    VISION = "vision_other"


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
    # Coding
    Tool("VibeCoding", Category.CODING),
    Tool("Tabby", Category.CODING),
    Tool("GitHub Copilot", Category.CODING),
    Tool("CodeWhisperer", Category.CODING),
    # Generative
    Tool("Stability AI", Category.GENERATIVE),
    Tool("RunwayML", Category.GENERATIVE),
    Tool("Midjourney", Category.GENERATIVE),
    Tool("DALL-E", Category.GENERATIVE),
    Tool("DreamStudio", Category.GENERATIVE),
    # NLP/LLMs
    Tool("DeepSeek", Category.NLP),
    Tool("Llama", Category.NLP),
    Tool("Hugging Face Transformers", Category.NLP),
    Tool("GPT-NeoX", Category.NLP),
    # Vision/Other
    Tool("MediaPipe", Category.VISION),
    Tool("OpenCV", Category.VISION),
    Tool("Segment Anything", Category.VISION),
]


def tools_by_category() -> Mapping[Category, List[str]]:
    """Return a mapping from category to list of tool names."""
    by_cat: Dict[Category, List[str]] = {c: [] for c in Category}
    for tool in TOOLS:
        by_cat[tool.category].append(tool.name)
    return by_cat
