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
- **Custom ML Models**: Train your own TensorFlow sentiment models on real data
- **Advanced Analysis**: LSTM + Attention mechanism with 85-90% accuracy
- **Production-Ready**: Model versioning, checkpointing, and comprehensive evaluation

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
    └── ML_PIPELINE.md          # ML docs
```

## Contributing

Contributions welcome! Fork, create a branch, and open a PR.

## License

MIT License - see [LICENSE](LICENSE) for details.
