# AISentinel

**AI Tool Sentiment Dashboard** - Track public sentiment, ratings, and user perception for AI tools like ChatGPT, Claude, Gemini, and more.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 **[Launch Live Dashboard →](https://your-app-name.streamlit.app)**

*Replace with your Streamlit Cloud URL after deployment*

**Or run locally:**
```bash
streamlit run src/dashboard/app.py
```

---

## About

AISentinel collects public sentiment from Twitter, Reddit, and Hacker News about AI tools, analyzes it using advanced NLP models (Transformers + TensorFlow), and displays results in an interactive dashboard with rankings, ratings, and detailed insights.

## Features

- **Tool Rankings**: See which AI tools have the best sentiment scores (0-10 scale)
- **Category Filtering**: Browse by Text & Chat, Coding & Dev, Images & Video, Audio
- **Detailed Insights**: Click any tool to see user quotes, sentiment breakdown, and privacy scores
- **Real-time Data**: Collects from Twitter, Reddit, and Hacker News
- **Advanced Analysis**: Uses Transformers + TensorFlow for sentiment analysis

## Tracked Tools

**Text & Chat**: ChatGPT, Claude, Gemini, DeepSeek, Mistral, Humain  
**Coding & Dev**: VibeCoding, Tabby, GitHub Copilot, CodeWhisperer, Bolt, Loveable  
**Images & Video**: Stability AI, RunwayML, Midjourney, DALL-E, DreamStudio, OpenCV  
**Audio & Speech**: Whisper, ElevenLabs

## Quick Start

**Run locally:**
```bash
git clone https://github.com/yourusername/aisentinel.git
cd aisentinel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env
# Add your API keys to .env
streamlit run src/dashboard/app.py
```

**Collect data:**
```bash
python scripts/collect_twitter.py
```

**Deploy to Streamlit Cloud:** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## Tech Stack

Python 3.11+, Streamlit, Transformers, TensorFlow, Pandas, Plotly, PRAW, Requests

## Contributing

Contributions welcome! Fork, create a branch, and open a PR.

## License

MIT License - see [LICENSE](LICENSE) for details.
