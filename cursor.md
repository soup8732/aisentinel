Project: AISentinel

Context for AI assistants:
- Code lives under `src/` with typed modules.
- Configuration via `src/utils/config.py` (dataclasses + env vars).
- Taxonomy in `src/utils/taxonomy.py` enumerates categories, tools, and sources.
- Collectors under `src/data_collection/sources/` (Twitter, Reddit, GitHub, Product Hunt, Discord stubs).
- Sentiment analyzers under `src/sentiment_analysis/` with `models/transformers_model.py` placeholder.
- Streamlit dashboard demo at `src/dashboard/app.py`.

Data & Flow:
- Collect → clean/dedupe → tag (category/tool) → analyze (sentiment) → visualize.
- Consider multi-class sentiment (e.g., excitement, disappointment, neutral).

Conventions:
- Python 3.11+, type hints + Google-style docstrings.
- Ruff/Black/isort/mypy configured in `pyproject.toml`.
- Tests in `tests/` mirror `src/` structure.
