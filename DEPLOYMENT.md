# Deployment Guide

## Streamlit Cloud Deployment

### Quick Deploy

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**
   - Sign in with your GitHub account
   - Click "New app"

3. **Configure your app:**
   - **Repository**: Select your `aisentinel` repository
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `src/dashboard/app.py`
   - **Python version**: `3.11`

4. **Add secrets** (in Streamlit Cloud dashboard):
   Go to Settings → Secrets and add:
   ```
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   REDDIT_CLIENT_ID=your_reddit_client_id (optional)
   REDDIT_CLIENT_SECRET=your_reddit_client_secret (optional)
   REDDIT_USER_AGENT=aisentinel/0.1.0 (optional)
   ```

5. **Deploy!**
   - Click "Deploy"
   - Wait for build to complete
   - Your app will be live at `https://your-app-name.streamlit.app`

### Requirements File

Streamlit Cloud automatically detects `requirements.txt` or `requirements/base.txt`. Make sure your `requirements/base.txt` includes all necessary dependencies.

### Environment Variables

All environment variables from `.env.example` can be set as secrets in Streamlit Cloud. The app will automatically load them.

### Troubleshooting

**Build fails:**
- Check Python version matches (3.11+)
- Verify all dependencies are in `requirements/base.txt`
- Check for import errors in logs

**App runs but shows errors:**
- Verify API keys are set in Streamlit Cloud secrets
- Check data file paths (`data/processed/sentiment.csv`)
- Review Streamlit Cloud logs for errors

**No data showing:**
- Run data collection scripts locally first
- Or add demo data to `data/processed/sentiment.csv` and commit it

## Docker Deployment

### Build and run locally:
```bash
docker-compose up --build
```

### Deploy to production:
1. Build image: `docker build -t aisentinel .`
2. Push to container registry (Docker Hub, AWS ECR, etc.)
3. Deploy to your hosting platform (AWS, GCP, Azure, etc.)

## Local Development

For local development, see the [README.md](README.md) Getting Started section.

