# AISentinel Documentation

AISentinel is an AI sentiment analysis project tracking public perception across AI domains (coding assistants, generative media, NLP/LLMs, vision). It provides data collection, analysis, and visualization components.

## Overview

- Data collection: Reddit (PRAW), Twitter (API v2), Hacker News (Algolia API)
- Analysis: Transformers + optional TensorFlow head, batch processing, confidence scoring
- Dashboard: Streamlit + Plotly (filters, distributions, trends, comparisons, word clouds)
- Packaging: `pyproject.toml` (Python 3.11+)
- Config: environment variables via `.env` and `src/utils/config.py`
- Testing: Pytest with smoke tests and unit tests
- CI/CD: GitHub Actions (lint, type-check, tests)
- Container: Dockerfile + docker-compose

## Quickstart

1. Create `.env` from `.env.example` and fill credentials.
2. Install: `pip install -r requirements/dev.txt`
3. Run tests: `pytest`
4. Launch dashboard: `streamlit run src/dashboard/app.py`

## Extending

- Add new tools/sources in `src/utils/taxonomy.py`.
- Implement new collectors under `src/data_collection/`.
- Swap in different transformer models or fine-tuned checkpoints in analyzers.

