"""
ArtificialAnalysis.ai API client for fetching technical information on AI tools and models.

This module provides access to comprehensive evaluations, benchmarks, and technical
specifications for various AI models and tools from ArtificialAnalysis.ai.

Requirements:
    - requests library (already in requirements)
    - API key in .env file:
        AA_API_KEY=your_api_key

Setup: Visit https://artificialanalysis.ai/ to obtain an API key.

Usage:
    from src.data_collection.artificialanalysis_client import ArtificialAnalysisClient

    client = ArtificialAnalysisClient()
    
    # Fetch all LLM models
    models = client.get_models()
    
    # Get specific model details (by ID, slug, or name)
    model_info = client.get_model_details("o3-mini")
    
    # Get evaluation scores for a model
    evaluations = client.get_model_evaluations("o3-mini")
    
    # Search models
    results = client.search_models("gpt")
    
    # Get models by creator
    openai_models = client.get_models_by_creator("OpenAI")
    
    # Media endpoints
    image_models = client.get_text_to_image_models(include_categories=True)
    video_models = client.get_text_to_video_models()
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional
import requests
from requests.adapters import HTTPAdapter

try:
    from urllib3.util.retry import Retry
except ImportError:
    # urllib3 is usually included with requests, but handle gracefully
    Retry = None  # type: ignore

from src.utils.config import load_config


@dataclass(frozen=True)
class ModelInfo:
    """Technical information about an AI model from ArtificialAnalysis.ai.

    Based on the actual API response structure from:
    https://artificialanalysis.ai/documentation#free-api
    """

    id: str
    name: str
    slug: Optional[str]
    model_creator: Optional[Dict[str, Any]]  # Contains id, name, slug
    evaluations: Optional[Dict[str, Any]]  # Benchmark scores
    pricing: Optional[Dict[str, Any]]  # Price per million tokens
    median_output_tokens_per_second: Optional[float]
    median_time_to_first_token_seconds: Optional[float]
    raw_data: Dict[str, Any]  # Full raw response for flexibility


class ArtificialAnalysisClient:
    """Client for interacting with ArtificialAnalysis.ai API.

    Provides methods to fetch technical information, benchmarks, and evaluations
    for various AI models and tools.
    """

    BASE_URL = "https://artificialanalysis.ai/api/v2"
    
    def __init__(self, timeout: int = 30) -> None:
        """Initialize the client with API credentials from config.

        Args:
            timeout: Request timeout in seconds.
        """
        self.cfg = load_config()
        self.timeout = timeout
        self.api_key = self.cfg.apis.artificialanalysis_api_key
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy if urllib3 is available
        if Retry is not None:
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
        
        return session

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an API request and return JSON response.

        Rate limit: 1,000 requests per day (per API documentation).

        Args:
            endpoint: API endpoint path (relative to BASE_URL).
            params: Optional query parameters.

        Returns:
            JSON response as dictionary.

        Raises:
            ValueError: If API key is not configured or invalid.
            requests.RequestException: If the API request fails.
        """
        if not self.api_key:
            raise ValueError(
                "AA_API_KEY is not set. Visit https://artificialanalysis.ai/ to get an API key."
            )

        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        try:
            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError("Invalid API key. Please check your AA_API_KEY.") from e
            elif response.status_code == 429:
                # Rate limit exceeded - API returns retry info
                try:
                    error_data = response.json()
                    retry_after = error_data.get("retryAfter", 3600)
                    raise requests.RequestException(
                        f"Rate limit exceeded. Retry after {retry_after} seconds. "
                        f"Limit: {error_data.get('limit', 1000)} requests/day."
                    ) from e
                except Exception:
                    raise requests.RequestException(
                        "Rate limit exceeded. Free API limit: 1,000 requests/day."
                    ) from e
            raise requests.RequestException(f"API request failed: {e}") from e
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Failed to connect to API: {e}") from e

    def get_models(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch list of all available LLM models.

        According to API docs: https://artificialanalysis.ai/documentation#free-api
        Response structure: { "status": 200, "data": [...] }

        Args:
            limit: Optional limit on number of models to return (client-side).

        Returns:
            List of model dictionaries with technical information.
        """
        response = self._make_request("data/llms/models")
        
        # API returns: { "status": 200, "data": [...] }
        if isinstance(response, dict) and "data" in response:
            models = response["data"]
            if limit and isinstance(models, list):
                return models[:limit]
            return models if isinstance(models, list) else []
        
        return []

    def get_model_details(self, model_id: str) -> Optional[ModelInfo]:
        """Get detailed technical information for a specific model.

        Note: The API doesn't have individual model endpoints, so we search
        through all models to find a match by ID, slug, or name.

        Args:
            model_id: The model identifier (UUID, slug, or name).

        Returns:
            ModelInfo object with technical details, or None if not found.
        """
        models = self.get_models()
        model_id_lower = model_id.lower()
        
        # Search by ID, slug, or name
        for model_data in models:
            if (model_data.get("id") == model_id or 
                model_data.get("slug", "").lower() == model_id_lower or
                model_data.get("name", "").lower() == model_id_lower):
                return self._parse_model_info(model_data)
        
        return None

    def get_model_evaluations(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get evaluation/benchmark results for a specific model.

        Args:
            model_id: The model identifier (UUID, slug, or name).

        Returns:
            Dictionary containing evaluation scores, or None if not found.
        """
        model_info = self.get_model_details(model_id)
        if model_info and model_info.evaluations:
            return model_info.evaluations
        return None

    def get_model_benchmarks(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Alias for get_model_evaluations() for backward compatibility.

        Args:
            model_id: The model identifier.

        Returns:
            Dictionary containing evaluation scores, or None if not found.
        """
        return self.get_model_evaluations(model_id)

    def search_models(self, query: str, creator: Optional[str] = None) -> List[ModelInfo]:
        """Search for models by name, slug, or creator.

        Args:
            query: Search query string (searches in name and slug).
            creator: Optional creator name filter.

        Returns:
            List of matching ModelInfo objects.
        """
        models = self.get_models()
        query_lower = query.lower()
        
        matching = []
        for model_data in models:
            name = model_data.get("name", "").lower()
            slug = model_data.get("slug", "").lower()
            creator_info = model_data.get("model_creator", {})
            creator_name = creator_info.get("name", "").lower() if isinstance(creator_info, dict) else ""
            
            # Check if query matches name or slug
            if query_lower in name or query_lower in slug:
                # Apply creator filter if provided
                if creator is None or creator.lower() in creator_name:
                    model_info = self._parse_model_info(model_data)
                    if model_info:
                        matching.append(model_info)
        
        return matching

    def get_models_by_creator(self, creator_name: str) -> List[ModelInfo]:
        """Get all models from a specific creator/provider.

        Args:
            creator_name: Creator name (e.g., "OpenAI", "Anthropic", "Google").

        Returns:
            List of ModelInfo objects from the specified creator.
        """
        models = self.get_models()
        creator_lower = creator_name.lower()
        
        matching = []
        for model_data in models:
            creator_info = model_data.get("model_creator", {})
            if isinstance(creator_info, dict):
                creator = creator_info.get("name", "").lower()
                if creator_lower in creator:
                    model_info = self._parse_model_info(model_data)
                    if model_info:
                        matching.append(model_info)
        
        return matching

    def _parse_model_info(self, data: Dict[str, Any]) -> Optional[ModelInfo]:
        """Parse raw API response into ModelInfo object.

        Based on actual API structure from:
        https://artificialanalysis.ai/documentation#free-api

        Args:
            data: Raw model data from API response.

        Returns:
            ModelInfo object or None if parsing fails.
        """
        try:
            return ModelInfo(
                id=data.get("id", ""),
                name=data.get("name", ""),
                slug=data.get("slug"),
                model_creator=data.get("model_creator"),
                evaluations=data.get("evaluations"),
                pricing=data.get("pricing"),
                median_output_tokens_per_second=data.get("median_output_tokens_per_second"),
                median_time_to_first_token_seconds=data.get("median_time_to_first_token_seconds"),
                raw_data=data
            )
        except Exception:
            return None

    def get_all_technical_info(self) -> Dict[str, ModelInfo]:
        """Fetch all available technical information for all LLM models.

        Returns:
            Dictionary mapping model IDs to ModelInfo objects.
        """
        models = self.get_models()
        result = {}
        
        for model_data in models:
            model_info = self._parse_model_info(model_data)
            if model_info:
                result[model_info.id] = model_info
        
        return result

    # Media Endpoints (Text-to-Image, Text-to-Speech, etc.)

    def get_text_to_image_models(self, include_categories: bool = False) -> List[Dict[str, Any]]:
        """Fetch text-to-image models with ELO ratings.

        Args:
            include_categories: If True, includes category breakdowns in response.

        Returns:
            List of text-to-image model dictionaries with ELO ratings.
        """
        params = {}
        if include_categories:
            params["include_categories"] = "true"
        
        response = self._make_request("data/media/text-to-image", params=params)
        if isinstance(response, dict) and "data" in response:
            return response["data"] if isinstance(response["data"], list) else []
        return []

    def get_image_editing_models(self) -> List[Dict[str, Any]]:
        """Fetch image editing models with ELO ratings.

        Returns:
            List of image editing model dictionaries with ELO ratings.
        """
        response = self._make_request("data/media/image-editing")
        if isinstance(response, dict) and "data" in response:
            return response["data"] if isinstance(response["data"], list) else []
        return []

    def get_text_to_speech_models(self) -> List[Dict[str, Any]]:
        """Fetch text-to-speech models with ELO ratings.

        Returns:
            List of text-to-speech model dictionaries with ELO ratings.
        """
        response = self._make_request("data/media/text-to-speech")
        if isinstance(response, dict) and "data" in response:
            return response["data"] if isinstance(response["data"], list) else []
        return []

    def get_text_to_video_models(self, include_categories: bool = False) -> List[Dict[str, Any]]:
        """Fetch text-to-video models with ELO ratings.

        Args:
            include_categories: If True, includes category breakdowns in response.

        Returns:
            List of text-to-video model dictionaries with ELO ratings.
        """
        params = {}
        if include_categories:
            params["include_categories"] = "true"
        
        response = self._make_request("data/media/text-to-video", params=params)
        if isinstance(response, dict) and "data" in response:
            return response["data"] if isinstance(response["data"], list) else []
        return []

    def get_image_to_video_models(self, include_categories: bool = False) -> List[Dict[str, Any]]:
        """Fetch image-to-video models with ELO ratings.

        Args:
            include_categories: If True, includes category breakdowns in response.

        Returns:
            List of image-to-video model dictionaries with ELO ratings.
        """
        params = {}
        if include_categories:
            params["include_categories"] = "true"
        
        response = self._make_request("data/media/image-to-video", params=params)
        if isinstance(response, dict) and "data" in response:
            return response["data"] if isinstance(response["data"], list) else []
        return []

