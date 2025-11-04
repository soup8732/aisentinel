# AISentinel

AISentinel provides a modular pipeline to collect public sentiment about AI tools across domains (coding assistants, generative media, NLP/LLMs, vision/other), analyze it, and visualize trends.

## Categories & Tools (tracked examples)

- Coding Assistants: VibeCoding, Tabby, GitHub Copilot, CodeWhisperer
- Generative Image/Video: Stability AI, RunwayML, Midjourney, DALL-E, DreamStudio
- NLP/LLMs: DeepSeek, Llama, Hugging Face Transformers, GPT-NeoX
- Vision/Other: MediaPipe, OpenCV, Segment Anything

## Data Sources

- Twitter/X, Reddit, Hacker News
- GitHub Issues/Discussions
- Product Hunt, AI forums, Discord server summaries

## Project Flow

1. Collect posts/comments referencing tools by keyword/hashtag.
2. Clean, normalize, and deduplicate; tag each item with category + tool.
3. Run sentiment analysis (baseline transformer or fine-tuned model).
4. Optionally multi-class sentiment (e.g., excitement, disappointment, neutral).
5. Visualize sentiment by category and tool, trends over time, keywords.

## Dashboard Ideas

- Sentiment by category and by tool
- Time-series trends and trending keywords
- Top positive/negative aspects (word clouds or key phrases)
- Filters: platform/source, tool, category, date range

## Tech Stack

- Python: Pandas, Requests; BeautifulSoup/Tweepy/PRAW for scraping/APIs
- NLP: Transformers/TensorFlow; scikit-learn for baselines
- App: Streamlit/Gradio/FastAPI (Streamlit demo included)

## Project Structure

```
.github/workflows/
requirements/
  base.txt
  dev.txt
src/
  data_collection/
    sources/
      twitter.py
      reddit.py
      github.py
      producthunt.py
      discord.py
  sentiment_analysis/
    models/
      transformers_model.py
  dashboard/
    app.py
  utils/
    config.py
    taxonomy.py
data/
  raw/
  processed/
  samples/
notebooks/
scripts/
docs/
tests/
```

## Getting Started

1. Create and activate a virtual environment (Python 3.11+ recommended).
2. Install dependencies:
   - Runtime: `pip install -r requirements/base.txt`
   - Dev: `pip install -r requirements/dev.txt`
3. Configure environment variables:
   - Copy `.env.example` to `.env` and fill in values.
4. (Optional) Verify configuration loading:
   ```bash
   python -c "from src.utils.config import load_config; print(load_config())"
   ```
5. Run the demo dashboard:
   ```bash
   streamlit run src/dashboard/app.py
   ```

## Why This Project?

- Demonstrates awareness across AI ecosystems and sentiment analysis
- Combines data engineering, NLP, and visualization
- Easy to extend with more tools/sources/models
- Great for portfolios and interactive demos

## License

MIT
