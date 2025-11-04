# AISentinel

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Interactive AI Tool Sentiment Dashboard** - Track public sentiment, ratings, and user perception for AI tools like ChatGPT, Claude, Gemini, and more.

## 🚀 Try It Now!

**👉 [Launch Live Dashboard](https://your-app-name.streamlit.app)** *(Replace with your Streamlit Cloud URL after deployment)*

Or run locally:
```bash
streamlit run src/dashboard/app.py
```

AISentinel provides a modular pipeline to collect public sentiment about AI tools across domains, analyze it, and visualize trends through an interactive dashboard.

## 🎯 What This Tool Does

AISentinel is a **fully functional, interactive dashboard** that:

1. **Collects** public sentiment from Twitter, Reddit, and Hacker News about AI tools
2. **Analyzes** sentiment using advanced NLP models (Transformers + TensorFlow)
3. **Displays** results in an easy-to-understand dashboard with:
   - 📊 Tool rankings and ratings (0-10 scale)
   - 📈 Sentiment trends over time
   - 🎯 Category-based filtering (Text & Chat, Coding & Dev, Images & Video, Audio)
   - 🔍 Detailed tool pages with user quotes
   - 🔒 Privacy & security scoring

**Try it now** - Click the link above to see the live dashboard!

## 📊 Categories & Tools

- **Text & Chat**: ChatGPT, Claude, Gemini, DeepSeek, Mistral, Humain
- **Coding & Dev**: VibeCoding, Tabby, GitHub Copilot, CodeWhisperer, Bolt, Loveable
- **Images & Video**: Stability AI, RunwayML, Midjourney, DALL-E, DreamStudio, OpenCV
- **Audio & Speech**: Whisper, ElevenLabs

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

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/aisentinel.git
   cd aisentinel
   ```

2. **Create and activate a virtual environment** (Python 3.11+ recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements/dev.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys (Twitter Bearer Token, Reddit credentials, etc.)
   ```

5. **Run the dashboard:**
   ```bash
   streamlit run src/dashboard/app.py
   ```
   Open http://localhost:8501 in your browser.

### Deploy to Streamlit Cloud

1. **Fork this repository** on GitHub
2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**
3. **Click "New app"** and select your fork
4. **Set app details:**
   - Main file path: `src/dashboard/app.py`
   - Python version: 3.11
5. **Add secrets** (in Streamlit Cloud dashboard):
   - `TWITTER_BEARER_TOKEN`: Your Twitter API bearer token
   - `REDDIT_CLIENT_ID`: Your Reddit client ID (optional)
   - `REDDIT_CLIENT_SECRET`: Your Reddit client secret (optional)
6. **Deploy!** Your app will be live at `https://your-app-name.streamlit.app`

### Collect Data

To collect real data from Twitter/Reddit/Hacker News:

```bash
# Test Twitter connection
python scripts/test_twitter.py

# Collect Twitter data for dashboard
python scripts/collect_twitter.py
```

The dashboard will automatically load data from `data/processed/sentiment.csv`.

## 🌐 Live Demo

**👉 [Click here to view the live dashboard](https://your-app-name.streamlit.app)**

*Once you deploy to Streamlit Cloud, replace the URL above with your actual deployment URL.*

The dashboard features:
- ✅ Real-time sentiment analysis
- ✅ Tool rankings and comparisons
- ✅ Category-based filtering
- ✅ Interactive tool details pages
- ✅ Privacy & security scoring

## 📸 Screenshots

Add screenshots of your dashboard here to showcase the UI:
- Dashboard home page
- Tool details view
- Category filtering

## 🛠️ Tech Stack

- **Python 3.11+**: Core language
- **Streamlit**: Interactive dashboard framework
- **Transformers**: Hugging Face models for sentiment analysis
- **TensorFlow**: Optional deep learning backend
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **PRAW**: Reddit API integration
- **Requests**: HTTP client for APIs

## 🧪 Testing

Run the test suite:
```bash
pytest
```

Check code quality:
```bash
ruff check .
black --check .
mypy src
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses [Hugging Face Transformers](https://huggingface.co/transformers/)
- Data sources: Twitter API, Reddit API, Hacker News Algolia API
