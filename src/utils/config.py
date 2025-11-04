from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional
import os

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional at runtime if not installed
    load_dotenv = None  # type: ignore[assignment]


@dataclass(frozen=True)
class PathsConfig:
    """Filesystem paths used by the application.

    Attributes:
        data_dir: Root data directory.
        raw_dir: Directory containing raw input data.
        processed_dir: Directory containing processed data artifacts.
        samples_dir: Directory containing small sample datasets.
    """

    data_dir: Path
    raw_dir: Path
    processed_dir: Path
    samples_dir: Path


@dataclass(frozen=True)
class APISettings:
    """API credentials and tokens.

    Attributes:
        openai_api_key: API key for OpenAI.
        huggingface_api_token: Access token for Hugging Face.
        twitter_bearer_token: Bearer token for Twitter API.
        reddit_client_id: Reddit application client id.
        reddit_client_secret: Reddit application client secret.
        reddit_user_agent: User agent for Reddit API requests.
    """

    openai_api_key: Optional[str]
    huggingface_api_token: Optional[str]
    twitter_bearer_token: Optional[str]
    reddit_client_id: Optional[str]
    reddit_client_secret: Optional[str]
    reddit_user_agent: Optional[str]


@dataclass(frozen=True)
class AppConfig:
    """Top-level application configuration.

    Attributes:
        environment: Current runtime environment (e.g., development, staging, production).
        paths: Grouped filesystem paths.
        apis: Grouped API credentials.
    """

    environment: str
    paths: PathsConfig
    apis: APISettings


def _get_env(env: Mapping[str, str], key: str, default: Optional[str] = None) -> Optional[str]:
    """Return an environment variable, falling back to a default if missing.

    Args:
        env: Environment mapping (typically os.environ).
        key: Environment variable name.
        default: Default value if the key is not set or empty.

    Returns:
        The environment variable value or the provided default.
    """
    value = env.get(key, "").strip()
    if value == "":
        return default
    return value


def load_config(env_file: Optional[Path] = None) -> AppConfig:
    """Load configuration from environment variables and optional .env file.

    If `env_file` is provided and exists, it will be loaded (requires python-dotenv).

    Args:
        env_file: Optional path to a .env file to load before reading variables.

    Returns:
        A fully-populated `AppConfig` instance.
    """
    if env_file is not None and env_file.exists() and load_dotenv is not None:
        load_dotenv(dotenv_path=str(env_file))
    elif env_file is None and load_dotenv is not None:
        # Load default .env if present
        default_env = Path(".env")
        if default_env.exists():
            load_dotenv(dotenv_path=str(default_env))

    environment = _get_env(os.environ, "ENVIRONMENT", default="development") or "development"

    data_dir = Path(_get_env(os.environ, "DATA_DIR", default="./data") or "./data").resolve()
    raw_dir = Path(_get_env(os.environ, "RAW_DATA_DIR", default=str(data_dir / "raw")) or str(data_dir / "raw")).resolve()
    processed_dir = Path(
        _get_env(os.environ, "PROCESSED_DATA_DIR", default=str(data_dir / "processed"))
        or str(data_dir / "processed")
    ).resolve()
    samples_dir = Path(
        _get_env(os.environ, "SAMPLES_DATA_DIR", default=str(data_dir / "samples"))
        or str(data_dir / "samples")
    ).resolve()

    paths = PathsConfig(
        data_dir=data_dir,
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        samples_dir=samples_dir,
    )

    apis = APISettings(
        openai_api_key=_get_env(os.environ, "OPENAI_API_KEY"),
        huggingface_api_token=_get_env(os.environ, "HUGGINGFACE_API_TOKEN"),
        twitter_bearer_token=_get_env(os.environ, "TWITTER_BEARER_TOKEN"),
        reddit_client_id=_get_env(os.environ, "REDDIT_CLIENT_ID"),
        reddit_client_secret=_get_env(os.environ, "REDDIT_CLIENT_SECRET"),
        reddit_user_agent=_get_env(os.environ, "REDDIT_USER_AGENT", default="aisentinel/0.1.0"),
    )

    return AppConfig(environment=environment, paths=paths, apis=apis)
