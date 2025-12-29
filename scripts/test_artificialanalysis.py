#!/usr/bin/env python3
"""
Test script for ArtificialAnalysis.ai API integration.

This script tests the API connection and displays sample technical information
about AI models and tools.

Usage:
    python scripts/test_artificialanalysis.py

Requirements:
    - AA_API_KEY environment variable set (or in .env file)
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection.artificialanalysis_client import ArtificialAnalysisClient


def main():
    """Test the ArtificialAnalysis API client."""
    print("=" * 60)
    print("ArtificialAnalysis.ai API Test")
    print("=" * 60)
    print()

    try:
        # Initialize client
        print("Initializing client...")
        client = ArtificialAnalysisClient()
        print("✓ Client initialized successfully")
        print()

        # Test: Get all models
        print("Fetching models list...")
        models = client.get_models(limit=10)
        print(f"✓ Retrieved {len(models)} models")
        print()

        if models:
            # Display first few models
            print("Sample models:")
            print("-" * 60)
            for i, model_data in enumerate(models[:5], 1):
                model_id = model_data.get("id", "N/A")
                model_name = model_data.get("name", "N/A")
                creator_info = model_data.get("model_creator", {})
                creator_name = creator_info.get("name", "N/A") if isinstance(creator_info, dict) else "N/A"
                print(f"{i}. {model_name}")
                print(f"   ID: {model_id}")
                print(f"   Creator: {creator_name}")
                if "evaluations" in model_data:
                    print(f"   Evaluations: Available")
                if "pricing" in model_data:
                    print(f"   Pricing: Available")
                print()

            # Test: Get details for first model
            if models:
                first_model = models[0]
                model_id = first_model.get("id")
                model_name = first_model.get("name", "")
                identifier = model_id or model_name
                
                if identifier:
                    print(f"Fetching detailed info for: {identifier}")
                    print("-" * 60)
                    model_info = client.get_model_details(identifier)
                    if model_info:
                        print(f"✓ Model: {model_info.name}")
                        print(f"  ID: {model_info.id}")
                        print(f"  Slug: {model_info.slug or 'N/A'}")
                        if model_info.model_creator:
                            creator = model_info.model_creator
                            print(f"  Creator: {creator.get('name', 'N/A')} ({creator.get('id', 'N/A')})")
                        if model_info.evaluations:
                            print(f"  Evaluations: {len(model_info.evaluations)} metrics available")
                            # Show a few evaluation scores
                            eval_items = list(model_info.evaluations.items())[:3]
                            for key, value in eval_items:
                                print(f"    - {key}: {value}")
                        if model_info.pricing:
                            pricing = model_info.pricing
                            print(f"  Pricing:")
                            if "price_1m_input_tokens" in pricing:
                                print(f"    Input: ${pricing['price_1m_input_tokens']}/1M tokens")
                            if "price_1m_output_tokens" in pricing:
                                print(f"    Output: ${pricing['price_1m_output_tokens']}/1M tokens")
                        if model_info.median_output_tokens_per_second:
                            print(f"  Speed: {model_info.median_output_tokens_per_second:.1f} tokens/sec")
                    else:
                        print("✗ Could not parse model details")
                    print()

        # Test: Search functionality
        print("Testing search functionality...")
        print("-" * 60)
        search_results = client.search_models("gpt")
        if search_results:
            print(f"✓ Found {len(search_results)} models matching 'gpt'")
            for result in search_results[:3]:
                creator = result.model_creator.get("name", "N/A") if result.model_creator else "N/A"
                print(f"  - {result.name} (by {creator})")
        else:
            print("  No results found for 'gpt'")
        print()

        # Test: Media endpoints
        print("Testing media endpoints...")
        print("-" * 60)
        try:
            image_models = client.get_text_to_image_models()
            if image_models:
                print(f"✓ Found {len(image_models)} text-to-image models")
                if image_models:
                    first_image = image_models[0]
                    print(f"  Top model: {first_image.get('name', 'N/A')} (ELO: {first_image.get('elo', 'N/A')})")
        except Exception as e:
            print(f"  Note: {e}")
        print()

        print("=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)

    except ValueError as e:
        print(f"✗ Configuration Error: {e}")
        print("\nPlease set AA_API_KEY in your .env file or environment variables.")
        print("Visit https://artificialanalysis.ai/ to obtain an API key.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

