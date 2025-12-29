# AISentinel - API Setup & Data Collection Guide

Complete guide for setting up APIs and collecting real-world data.

## 📋 Table of Contents

1. [Overview](#overview)
2. [What You Need](#what-you-need)
3. [API Setup Instructions](#api-setup-instructions)
4. [Data Collection Methods](#data-collection-methods)
5. [Data Cleaning Pipeline](#data-cleaning-pipeline)
6. [Quick Start (No APIs Required)](#quick-start-no-apis-required)

---

## Overview

AISentinel supports **two modes**:

### Mode 1: ML Development (No APIs Required) ✅
Perfect for learning, portfolio building, and showcasing ML skills:
- Train custom sentiment models on public datasets
- Use pre-downloaded data (SST-2, IMDB)
- Test with synthetic AI tool reviews
- **NO API keys needed**
- **NO web scraping needed**

### Mode 2: Production Data Collection (APIs Required)
For real-time sentiment analysis of actual AI tool discussions:
- Collect live data from Twitter, Reddit, Hacker News
- Monitor real user opinions
- Requires API credentials

---

## What You Need

### For ML Training (Mode 1) - NOTHING! 🎉

You can train the complete ML pipeline with:
```bash
# Install dependencies
pip install -r requirements/base.txt

# Train model (downloads public datasets automatically)
python scripts/train_sentiment_model.py

# Test model
python scripts/test_model.py
```

**Zero configuration required!** The training pipeline:
- Auto-downloads SST-2 dataset (67K samples) via HuggingFace
- Auto-downloads IMDB dataset (15K samples) via HuggingFace
- Generates synthetic AI tool reviews (800 samples)
- Cleans and preprocesses everything
- No API keys, no web scraping, no manual data collection

### For Real-Time Data Collection (Mode 2)

| Service | Required? | Cost | Purpose |
|---------|-----------|------|---------|
| **Hacker News** | ❌ No API | FREE | Public Algolia API, no auth |
| **Twitter/X** | API Key | FREE (limited) | Real-time tweets |
| **Reddit** | API Key | FREE | Subreddit discussions |
| **ArtificialAnalysis** | API Key | Varies | Technical model info & benchmarks |
| OpenAI | ❌ Optional | Paid | Advanced features |
| HuggingFace | ❌ Optional | FREE | Public model access |

---

## API Setup Instructions

### 1. Hacker News (No Setup Required ✅)

**Cost**: FREE
**Setup**: None needed!

Hacker News uses the public Algolia search API. No authentication required.

```python
# Works immediately
from src.data_collection.hackernews_collector import HackerNewsCollector

collector = HackerNewsCollector(limit=100)
data = list(collector.collect())
```

**What you get**:
- Posts mentioning AI tools
- Comments and discussions
- Points and engagement metrics
- No rate limits (reasonable use)

---

### 2. Twitter/X API

**Cost**: FREE (Elevated Access required)
**Rate Limits**: 500K tweets/month (Free tier)

#### Setup Steps:

1. **Create Twitter Developer Account**
   - Go to: https://developer.twitter.com/
   - Sign up for a developer account
   - Complete the application form (explain your use case)

2. **Create a Project & App**
   - In the Developer Portal, create a new Project
   - Create an App within the project
   - Name it something like "AISentinel Data Collector"

3. **Request Elevated Access**
   - Go to your Project settings
   - Request "Elevated Access" (required for v2 API)
   - Explain: "Collecting public sentiment data about AI tools for analysis"
   - Approval usually takes 1-2 days

4. **Get Bearer Token**
   - In your App settings, go to "Keys and Tokens"
   - Generate a "Bearer Token"
   - Copy this token

5. **Add to .env**
   ```bash
   TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAABc1dQEAAAAA...
   ```

#### Test Your Setup:

```bash
# Test Twitter connection
python scripts/test_twitter.py
```

**What you get**:
- Recent tweets mentioning AI tools
- Tweet text, timestamps, engagement metrics
- Author information
- Retweets and replies

**Rate Limits**:
- 450 requests per 15 minutes
- 100 tweets per request
- ~45,000 tweets per 15 min window

---

### 3. Reddit API

**Cost**: FREE
**Rate Limits**: 60 requests/minute

#### Setup Steps:

1. **Create Reddit Account** (if you don't have one)
   - Sign up at https://reddit.com

2. **Create Reddit App**
   - Go to: https://www.reddit.com/prefs/apps
   - Scroll to bottom, click "Create App" or "Create Another App"
   - Fill in:
     - **Name**: AISentinel Data Collector
     - **Type**: Select "script"
     - **Description**: Collecting AI tool sentiment data
     - **About URL**: (leave blank)
     - **Redirect URI**: http://localhost:8080 (required but not used)
   - Click "Create App"

3. **Get Credentials**
   - **Client ID**: String under "personal use script" (looks like: `abc123xyz`)
   - **Client Secret**: String next to "secret" (looks like: `AbC123XyZ...`)

4. **Add to .env**
   ```bash
   REDDIT_CLIENT_ID=abc123xyz
   REDDIT_CLIENT_SECRET=AbC123XyZ456...
   REDDIT_USER_AGENT=aisentinel/0.1.0
   ```

#### Test Your Setup:

```python
from src.data_collection.reddit_collector import RedditCollector

collector = RedditCollector(
    subreddits=["MachineLearning", "OpenAI"],
    limit=50
)
data = list(collector.collect())
print(f"Collected {len(data)} items")
```

**What you get**:
- Posts from AI-related subreddits
- Comments and discussions
- Upvotes and engagement
- User sentiment and opinions

**Recommended Subreddits**:
- r/MachineLearning
- r/ArtificialIntelligence
- r/OpenAI
- r/ChatGPT
- r/LocalLLaMA
- r/StableDiffusion
- r/Midjourney

---

### 4. Optional: OpenAI API

**Cost**: Pay-per-use (starts at $0.002 per 1K tokens)
**Required**: No, only for advanced features

Not currently used in the base pipeline, but useful for:
- GPT-powered sentiment analysis
- Advanced text classification
- Zero-shot tool categorization

**Setup**:
1. Go to https://platform.openai.com/api-keys
2. Create an API key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

---

### 5. ArtificialAnalysis.ai API

**Cost**: Varies (check website for pricing)
**Required**: No, optional for technical model information

Provides comprehensive technical information, benchmarks, and evaluations for AI models and tools.

#### Setup Steps:

1. **Get API Key**
   - Visit: https://artificialanalysis.ai/
   - Sign up for an account
   - Navigate to API section to obtain your API key

2. **Add to .env**
   ```bash
   AA_API_KEY=your_api_key_here
   ```

#### Usage:

```python
from src.data_collection.artificialanalysis_client import ArtificialAnalysisClient

# Initialize client
client = ArtificialAnalysisClient()

# Get all LLM models
models = client.get_models()

# Get specific model details (by ID, slug, or name)
model_info = client.get_model_details("o3-mini")

# Get evaluation scores
evaluations = client.get_model_evaluations("o3-mini")

# Search for models
results = client.search_models("gpt")

# Get models by creator
openai_models = client.get_models_by_creator("OpenAI")

# Media endpoints
image_models = client.get_text_to_image_models(include_categories=True)
video_models = client.get_text_to_video_models()
speech_models = client.get_text_to_speech_models()
```

#### Test Your Setup:

```bash
python scripts/test_artificialanalysis.py
```

**What you get**:
- Technical specifications for AI models (LLMs)
- Evaluation scores and benchmark results
- Pricing information (per million tokens)
- Performance metrics (tokens/second, time to first token)
- Creator/provider information
- Media model rankings (text-to-image, text-to-video, etc.) with ELO ratings

**API Details**:
- Rate limit: 1,000 requests per day (free tier)
- Endpoints: LLMs, Text-to-Image, Image Editing, Text-to-Speech, Text-to-Video, Image-to-Video
- Response format: JSON with `status` and `data` fields
- Documentation: https://artificialanalysis.ai/documentation#free-api

---

### 6. Optional: HuggingFace Token

**Cost**: FREE
**Required**: No, public datasets work without auth

Only needed if you want to:
- Download private models
- Use gated datasets
- Increase download rate limits

**Setup**:
1. Go to https://huggingface.co/settings/tokens
2. Create a "Read" token
3. Add to `.env`: `HUGGINGFACE_API_TOKEN=hf_...`

---

## Data Collection Methods

### Method 1: Hacker News (Easiest - No Auth)

```python
from src.data_collection.hackernews_collector import HackerNewsCollector

collector = HackerNewsCollector(limit=100)
data = list(collector.collect())
# Returns: Posts and comments about AI tools
```

**Pros**:
- No API setup
- No rate limits
- High-quality technical discussions
- Free forever

**Cons**:
- Smaller volume than Twitter
- Tech-focused audience only

---

### Method 2: Twitter Collection

```python
from src.data_collection.twitter_collector import TwitterCollector

collector = TwitterCollector(limit=500)
tweets = list(collector.collect())
# Returns: Recent tweets about AI tools
```

**Pros**:
- Large volume of data
- Real-time sentiment
- Diverse user base
- Good engagement metrics

**Cons**:
- Requires API approval
- Rate limits
- More noise/spam

---

### Method 3: Reddit Collection

```python
from src.data_collection.reddit_collector import RedditCollector

collector = RedditCollector(
    subreddits=["MachineLearning", "ChatGPT"],
    limit=200,
    include_comments=True
)
posts = list(collector.collect())
# Returns: Posts and comments from subreddits
```

**Pros**:
- Detailed discussions
- Community moderation (less spam)
- Threaded conversations
- Topic-specific (subreddits)

**Cons**:
- Slower than Twitter
- Need to target right subreddits
- Less volume per subreddit

---

## Data Cleaning Pipeline

All collectors include **automatic data cleaning**:

### 1. Text Preprocessing

```python
def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)

    # Remove Twitter mentions
    text = re.sub(r'@\w+', '', text)

    # Clean hashtags (keep text, remove #)
    text = re.sub(r'#(\w+)', r'\1', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove special characters (keep punctuation)
    text = re.sub(r'[^\w\s.,!?-]', '', text)

    return text
```

### 2. Tool Extraction

Automatically identifies which AI tool is mentioned:

```python
def _infer_tool_category(text: str) -> tuple[str, Category]:
    """Extract tool name and category from text."""
    text_lower = text.lower()

    for category, tools in tools_by_category().items():
        for tool_name in tools:
            if tool_name.lower() in text_lower:
                return tool_name, category

    return None, None
```

### 3. Deduplication

```python
# Remove duplicate posts by ID
df = df.drop_duplicates(subset=["id"], keep="last")
```

### 4. Filtering

```python
# Remove very short texts (likely spam)
df = df[df["text"].str.len() > 10]

# Remove null values
df = df.dropna(subset=["text", "created_at"])

# Remove non-matching queries
df = df[df["text"].str.contains("ChatGPT|Claude|...", case=False)]
```

### 5. Timestamp Normalization

```python
# Convert all timestamps to UTC datetime
df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
df = df.dropna(subset=["created_at"])
```

---

## Quick Start (No APIs Required)

### Option A: Train ML Model Only

Perfect for portfolio/resume work:

```bash
# 1. Install dependencies
pip install -r requirements/base.txt

# 2. Prepare data (auto-downloads public datasets)
python src/data_collection/prepare_training_data.py

# 3. Train model
python scripts/train_sentiment_model.py

# 4. Test model
python scripts/test_model.py

# 5. Explore in Jupyter
jupyter notebook notebooks/model_evaluation.ipynb
```

**NO API KEYS NEEDED** ✅

---

### Option B: Collect Real Data

1. **Set up APIs** (follow instructions above)

2. **Create .env file**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Collect data**:
   ```bash
   # Hacker News (no API needed)
   python -c "
   from src.data_collection.hackernews_collector import HackerNewsCollector
   import pandas as pd

   collector = HackerNewsCollector(limit=100)
   data = list(collector.collect())
   pd.DataFrame(data).to_csv('data/raw/hackernews.csv', index=False)
   print(f'Collected {len(data)} items')
   "

   # Twitter (requires API)
   python scripts/collect_twitter.py

   # Reddit (requires API)
   python -c "
   from src.data_collection.reddit_collector import RedditCollector
   import pandas as pd

   collector = RedditCollector(limit=100)
   data = list(collector.collect())
   pd.DataFrame(data).to_csv('data/raw/reddit.csv', index=False)
   "
   ```

4. **Run dashboard**:
   ```bash
   streamlit run src/dashboard/app.py
   ```

---

## Web Scraping - NOT NEEDED ❌

**You do NOT need to do any web scraping!**

All data is collected through official APIs:
- ✅ Twitter: Official Twitter API v2
- ✅ Reddit: Official Reddit API (PRAW)
- ✅ Hacker News: Official Algolia API
- ✅ Training data: HuggingFace Datasets library

**Benefits**:
- No scraping infrastructure needed
- No proxy management
- No anti-bot detection
- No legal/ToS concerns
- Clean, structured data
- Rate limiting built-in

---

## Troubleshooting

### "TWITTER_BEARER_TOKEN not found"

**Solution**: Create `.env` file and add your token:
```bash
cp .env.example .env
# Edit .env and add: TWITTER_BEARER_TOKEN=your_token_here
```

### "Rate limit exceeded"

**Twitter**: Wait 15 minutes or reduce `limit` parameter
**Reddit**: Wait 1 minute or reduce request frequency
**Hacker News**: Should not happen, contact support if it does

### "No data collected"

**Check**:
1. API credentials are correct in `.env`
2. Internet connection is working
3. API keys have proper permissions
4. Rate limits not exceeded

**Debug**:
```python
from src.utils.config import load_config

cfg = load_config()
print(f"Twitter token: {cfg.apis.twitter_bearer_token[:10] if cfg.apis.twitter_bearer_token else 'Not set'}...")
print(f"Reddit ID: {cfg.apis.reddit_client_id}")
print(f"ArtificialAnalysis API key: {'Set' if cfg.apis.artificialanalysis_api_key else 'Not set'}")
```

### "HuggingFace datasets won't download"

**Solution**: Check internet connection. Datasets are large:
- SST-2: ~7 MB
- IMDB: ~65 MB

**Workaround**: Set cache directory:
```python
import os
os.environ['HF_HOME'] = '/path/to/cache'
```

---

## Summary

### For ML Development (Recommended for Portfolio):
- ✅ No APIs needed
- ✅ No web scraping
- ✅ No manual data collection
- ✅ Everything automated
- ✅ Ready to train in 5 minutes

### For Production:
- Twitter API: ~2 days approval wait
- Reddit API: Instant setup (5 minutes)
- Hacker News: Works immediately
- All data cleaning automated
- No web scraping required

**Start with ML training first** to build your portfolio, then add real-time data collection later!
