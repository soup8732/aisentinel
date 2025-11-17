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

### 📊 Interactive Dashboard
- **Tool Rankings**: See which AI tools have the best sentiment scores (0-10 scale)
- **Dual View Modes**: Toggle between Table view (data-dense) and Card view (visual)
- **Quick Jump Search**: Autocomplete dropdown to instantly find any tool
- **Advanced Filtering**: Category multi-select, date range filtering, and text search
- **Trend Indicators**: See at-a-glance if tools are improving (📈), declining (📉), or stable (➡)
- **CSV Export**: Download rankings and raw data for external analysis

### 📈 Analytics & Visualization
- **Sentiment Trends**: Interactive Plotly charts showing sentiment over time
- **Distribution Analysis**: Pie charts breaking down positive/neutral/negative mentions
- **Category Performance**: Compare sentiment scores across different AI tool categories
- **Tool Comparison**: Side-by-side comparison of any two tools with delta metrics

### 🔍 Detailed Insights
- **User Quotes**: Real positive, negative, and neutral mentions from users
- **Privacy Scores**: Dedicated privacy & security sentiment analysis
- **Perception Ratings**: User perception separate from general sentiment
- **Mention Tracking**: See total mentions and sentiment breakdown for each tool

### 🤖 Custom ML Models
- **TensorFlow Models**: Train your own sentiment models on real data
- **Advanced Architectures**: LSTM + Attention mechanism with 85-90% accuracy
- **Production-Ready**: Model versioning, checkpointing, and comprehensive evaluation
- **Real-time Inference**: Use custom models in production dashboard

### 📡 Data Collection
- **Multi-source**: Collects from Twitter, Reddit, and Hacker News
- **Automated Cleaning**: Built-in text preprocessing and deduplication
- **No Scraping**: All data from official APIs (legal and ethical)
- **Instant Start**: Hacker News collector works with zero setup

## Tracked Tools

**Text & Chat**: ChatGPT, Claude, Gemini, DeepSeek, Mistral, Jasper, Copy.ai, Writesonic, Lindy

**Coding & Dev**: GitHub Copilot, Amazon Q Developer, CodeWhisperer, Tabnine, Tabby, Replit Ghostwriter, Bolt, Loveable, JetBrains AI Assistant, Cursor, Codeium, Polycoder, AskCodi, Sourcery, Greta

**Images & Video**: Stability AI, RunwayML, Midjourney, DALL-E, DreamStudio, OpenCV, Adobe Firefly, Pika Labs, Luma Dream Machine, Vidu

**Audio & Speech**: Whisper, ElevenLabs, Murf AI, PlayHT, Speechify, Synthesys, Animaker, Kits AI, WellSaid Labs, Hume, DupDub

*This list is continuously updated as new AI tools emerge.*

## Quick Start

### 1. Setup

```bash
git clone https://github.com/yourusername/aisentinel.git
cd aisentinel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
```

### 2. Train Sentiment Model (Optional but Recommended)

```bash
# Prepare training data (downloads SST-2, IMDB datasets)
python src/data_collection/prepare_training_data.py

# Train custom TensorFlow model
python scripts/train_sentiment_model.py

# Test the trained model
python scripts/test_model.py
```

This trains a custom LSTM model with attention mechanism on 80K+ samples. Training takes ~10-15 minutes on CPU.

**Expected Results**:
- Overall accuracy: 85-90%
- Precision/Recall: 0.85-0.90
- Model saved to `models/run_YYYYMMDD_HHMMSS/`

See [docs/ML_PIPELINE.md](docs/ML_PIPELINE.md) for detailed ML documentation.

### 3. Run Dashboard

```bash
streamlit run src/dashboard/app.py
```

### 4. Collect Real Data (Optional)

```bash
cp .env.example .env
# Add your API keys to .env
python scripts/collect_twitter.py
```

**Deploy to Streamlit Cloud:** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## Tech Stack

**Core**: Python 3.11+, TensorFlow 2.17+, Transformers, Keras

**ML/Data**: NumPy, Pandas, scikit-learn, HuggingFace Datasets

**Visualization**: Streamlit, Plotly, Matplotlib, Seaborn

**Data Collection**: PRAW (Reddit), Requests (Twitter/HN)

**Models**: Custom LSTM + Attention, Transformer-based architectures

## Project Structure

```
aisentinel/
├── src/
│   ├── ml/                      # Machine learning models
│   │   ├── model.py            # Custom TF/Keras architectures
│   │   └── train_model.py      # Training pipeline
│   ├── sentiment_analysis/     # Sentiment analyzers
│   │   └── analyzer.py         # Production inference
│   ├── data_collection/        # Data collectors
│   │   └── prepare_training_data.py
│   ├── dashboard/              # Streamlit dashboard
│   │   └── app.py              # Main dashboard (5 tabs, Plotly charts)
│   └── utils/                  # Config, taxonomy
├── models/                      # Trained models & checkpoints
├── data/                        # Training & processed data
├── notebooks/                   # Jupyter notebooks
│   └── model_evaluation.ipynb  # Interactive analysis
├── scripts/                     # Utility scripts
│   ├── train_sentiment_model.py
│   └── test_model.py
├── tests/                       # Unit tests
└── docs/                        # Documentation
    ├── ML_PIPELINE.md          # ML architecture & training guide
    ├── API_SETUP.md            # API credentials setup guide
    ├── CODEBASE_AUDIT.md       # Full codebase audit report
    ├── FRONTEND_REVIEW.md      # Dashboard code review (A- grade)
    └── FRONTEND_FEATURES.md    # Complete feature guide (v2.0)
```

## Documentation

- **[Frontend Features Guide](docs/FRONTEND_FEATURES.md)** - Complete guide to all dashboard features (v2.0)
- **[ML Pipeline Guide](docs/ML_PIPELINE.md)** - Model architectures, training, and evaluation
- **[API Setup Guide](docs/API_SETUP.md)** - Detailed API credentials setup (Twitter, Reddit, HN)
- **[Codebase Audit](docs/CODEBASE_AUDIT.md)** - What works, what needs setup, quick start options
- **[Frontend Review](docs/FRONTEND_REVIEW.md)** - Detailed code review and technical analysis

## Contributing

Contributions welcome! Fork, create a branch, and open a PR.

## License

MIT License - see [LICENSE](LICENSE) for details.
