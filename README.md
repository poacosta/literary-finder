# The Literary Finder

**A Multi-Agent System for Deep Literary Discovery**

The Literary Finder is an advanced AI-powered system that transforms how readers discover and connect with authors. It leverages a multi-agent architecture to provide deep, contextual, and personalized narratives about your favorite writers.

---

## Quick Start (Docker-First)

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (required)
- Google Books API key (required for full features)

### 1. Clone the Repository

```bash
git clone https://github.com/poacosta/literary-finder.git
cd literary-finder
```

### 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
# Edit .env and set your API keys
```

**Required:**

- `OPENAI_API_KEY` (get from [OpenAI Platform](https://platform.openai.com/))
- `GOOGLE_API_KEY` (get from [Google Cloud Console](https://console.cloud.google.com/))

### 3. Launch with Docker (Recommended)

```bash
# Make sure your .env file contains your API keys
docker-compose up --build
```

The Gradio web interface will be available at [http://localhost:7860](http://localhost:7860)

#### Manual Docker Build

```bash
docker build -t literary-finder .
docker run -p 7860:7860 \
  -e OPENAI_API_KEY="your-key" \
  -e GOOGLE_API_KEY="your-key" \
  literary-finder
```

---

## Usage

### Web Interface (Gradio)

- Visit [http://localhost:7860](http://localhost:7860) after starting Docker
- Enter an author name and click "Analyze Author"
- Example authors: Virginia Woolf, Maya Angelou, Jorge Luis Borges

### API Server

The REST API is available at [http://localhost:8000](http://localhost:8000) (if started separately):

```bash
# Start API server (if not using Docker Compose)
uvicorn literary_finder.api.server:app --reload --host 0.0.0.0 --port 8000
```

API endpoints:
- `/analyze` (POST): Analyze an author
- `/health` (GET): Health check
- `/docs`: Interactive API docs

Example:

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"author_name": "Maya Angelou"}'
```

### Python API

```python
from literary_finder.orchestration import LiteraryFinderGraph

finder = LiteraryFinderGraph(llm_provider="openai")
result = finder.process_author("Octavia Butler")
if result["success"]:
    print(result["final_report"])
else:
    print(f"Error: {result['error']}")
```

---

## Architecture

The Literary Finder uses three specialized AI agents orchestrated by LangGraph:

- **Contextual Historian**: Investigates the author's life, influences, and historical era
- **Literary Cartographer**: Compiles bibliographies and reading maps using Google Books API
- **Legacy Connector**: Analyzes literary legacy, themes, and recommends similar authors

---

## Configuration

Edit your `.env` file with the following:

```env
# Required
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_books_api_key

# Optional
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=5
```

---

## Development

### Project Structure

```
literary_finder/
├── agents/              # AI agents (Historian, Cartographer, Legacy Connector)
├── api/                 # FastAPI REST server
├── interface/           # Gradio web interface
├── models/              # Pydantic data models
├── orchestration/       # LangGraph workflow
├── tools/               # External API integrations (OpenAI, Google Books)
└── app.py               # Main Gradio application
```

### Running Locally (Without Docker)

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

### Running Tests

```bash
pytest
# Or with coverage
pytest --cov=literary_finder
```

---

## Example Output

* See [Screenshots](screenshots)

---

## Troubleshooting

- **Missing API Keys**: Ensure `.env` is present and contains valid keys
- **Docker Issues**: Make sure Docker is running and ports 7860/8000 are available
- **Google Books API**: Ensure the API is enabled in your Google Cloud project
- **Web Search Not Working**: Your OpenAI API key must have web search access

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*The Literary Finder: Bridging the gap between readers and the vast world of literature, one author at a time.* 📚✨


[def]: './screenshoots'