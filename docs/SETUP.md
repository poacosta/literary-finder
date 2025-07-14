
# Setup Guide for The Literary Finder

This guide will help you get started with The Literary Finder, focusing on a Docker-first workflow. Local Python setup is still possible for advanced users.

## Prerequisites

- Docker and Docker Compose
- OpenAI API key (required)
- Google Books API key (required)

## 1. Clone the Repository

```bash
git clone https://github.com/poacosta/literary-finder.git
cd literary-finder
```

## 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
# Edit .env and set your API keys
```

**Required:**

- `OPENAI_API_KEY` (get from [OpenAI Platform](https://platform.openai.com/))
- `GOOGLE_API_KEY` (get from [Google Cloud Console](https://console.cloud.google.com/))

**Optional:**

- `ANTHROPIC_API_KEY` (for Claude support)
- `LOG_LEVEL`, `MAX_CONCURRENT_REQUESTS`, etc.

## 3. Launch with Docker (Recommended)

```bash
# Make sure your .env file contains your API keys
docker-compose up --build
```

The Gradio web interface will be available at [http://localhost:7860](http://localhost:7860)

### Manual Docker Build

```bash
docker build -t literary-finder .
docker run -p 7860:7860 \
  -e OPENAI_API_KEY="your-key" \
  -e GOOGLE_API_KEY="your-key" \
  literary-finder
```

## 4. Advanced: Local Python Setup (Optional)

If you want to develop or run Literary Finder without Docker:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# (Optional) Install dev dependencies
pip install -e ".[dev]"

# Launch Gradio app
python -m literary_finder.app
```

## 5. API Keys: How to Obtain

### OpenAI API Key
- Go to [OpenAI Platform](https://platform.openai.com/)
- Create an account or sign in
- Navigate to API Keys
- Create a new secret key (starts with `sk-`)

### Google Books API Key
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create/select a project
- Enable "Books API" in "APIs & Services > Library"
- Create credentials > API key

### Anthropic API Key (Optional)
- Go to [Anthropic Console](https://console.anthropic.com/)
- Create an account and get your API key

## 6. Troubleshooting

- **Missing API Keys**: Ensure `.env` is present and contains valid keys
- **Docker Issues**: Make sure Docker is running and ports 7860/8000 are available
- **Google Books API**: Ensure the API is enabled in your Google Cloud project
- **Web Search Not Working**: Your OpenAI API key must have web search access

## 7. Production Deployment

Set these in your `.env` for production:

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

## 8. Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **CORS**: Configure CORS properly for production
3. **Rate Limiting**: Implement proper rate limiting
4. **Input Validation**: The system includes basic validation, but consider additional security measures

## 9. Getting Help

1. Check logs for error messages
2. Verify all API keys are correctly configured
3. Test individual components (agents, tools) separately
4. Review the API documentation in `docs/API.md`
5. Check GitHub issues for similar problems

---

Happy literary discovery! 📚✨
