
# Literary Finder API Documentation

## Overview

The Literary Finder provides both REST API and Python API interfaces for analyzing authors and generating comprehensive literary reports.

---

## REST API

### Base URLs

- Gradio Web UI: [http://localhost:7860](http://localhost:7860) (default with Docker)
- REST API: [http://localhost:8000](http://localhost:8000) (if started separately)

### Endpoints

- `GET /health` — Health check
- `POST /analyze` — Analyze an author (main endpoint)
- `GET /analyze/{author_name}` — Quick author analysis
- `GET /docs` — Interactive API docs (Swagger UI)
- `GET /redoc` — ReDoc API docs

#### Example: Analyze an Author

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"author_name": "Maya Angelou"}'
```

**Request Body:**

```json
{
  "author_name": "Virginia Woolf",
  "llm_provider": "openai",
  "model_name": "gpt-4",
  "enable_parallel": true
}
```

**Response:**

```json
{
  "success": true,
  "author_name": "Virginia Woolf",
  "final_report": "# The Literary Finder: Virginia Woolf\n...",
  "processing_time_seconds": 45.67,
  "errors": []
}
```

---

## Python API

### Basic Usage

```python
from literary_finder.orchestration import LiteraryFinderGraph

finder = LiteraryFinderGraph(llm_provider="openai")
result = finder.process_author("Octavia Butler")
if result["success"]:
    print(result["final_report"])
else:
    print(f"Error: {result['error']}")
```

### Advanced Usage

```python
from literary_finder.orchestration import LiteraryFinderGraph
from literary_finder.agents import ContextualHistorian, LiteraryCartographer, LegacyConnector

finder = LiteraryFinderGraph(
    llm_provider="anthropic",
    model_name="claude-3-sonnet-20240229",
    enable_parallel=False
)

authors = ["Gabriel García Márquez", "Isabel Allende", "Jorge Luis Borges"]
for author in authors:
    result = finder.process_author(author)
    print(result["final_report"])
```

---

## Data Models

### AuthorRequest

```python
class AuthorRequest(BaseModel):
    author_name: str
    llm_provider: Optional[str] = "openai"
    model_name: Optional[str] = None
    enable_parallel: Optional[bool] = True
```

### AuthorResponse

```python
class AuthorResponse(BaseModel):
    success: bool
    author_name: str
    final_report: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    errors: List[str] = []
```

---

## Error Handling

**Missing API Keys:**

```json
{
  "success": false,
  "error": "OPENAI_API_KEY environment variable is required",
  "errors": ["Configuration error"]
}
```

**Invalid Author Name:**

```json
{
  "success": false,
  "error": "Author name is required and cannot be empty",
  "errors": ["Validation error"]
}
```

---

## Rate Limits & Best Practices

- Google Books API: 1000 requests/day (free tier)
- OpenAI API: Varies by plan
- Anthropic API: Varies by plan

**Tips:**

1. Use parallel processing for speed, sequential for quota savings
2. Always check the `success` field and handle `errors`
3. Monitor your API quotas
4. Never commit API keys to version control

---

## Examples

### CLI Script

```python
#!/usr/bin/env python3
import sys
from literary_finder.orchestration import LiteraryFinderGraph

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py 'Author Name'")
        sys.exit(1)
    author_name = sys.argv[1]
    finder = LiteraryFinderGraph()
    result = finder.process_author(author_name)
    if result["success"]:
        filename = f"{author_name.replace(' ', '_').lower()}_report.md"
        with open(filename, 'w') as f:
            f.write(result["final_report"])
        print(f"Report saved to {filename}")
    else:
        print(f"Error: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Web Integration Example

```python
from fastapi import FastAPI
from literary_finder.orchestration import LiteraryFinderGraph

app = FastAPI()
finder = LiteraryFinderGraph()

@app.post("/analyze/{author_name}")
async def analyze(author_name: str):
    result = finder.process_author(author_name)
    return result
```

---

## More

See the main README and `docs/SETUP.md` for full setup and usage details.
