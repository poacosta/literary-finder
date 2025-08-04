# The Literary Finder 📖🔍

**A Multi-Agent System for Deep Literary Discovery**

The Literary Finder is an AI-powered system that transforms how readers discover and connect with authors. It leverages a multi-agent architecture to provide deep, contextual, and personalized narratives about your favorite writers.

## Official Publication

- [The Literary Finder: A Multi-Agent System for Deep Literary Discovery](https://app.readytensor.ai/publications/the-literary-finder-a-multi-agent-system-for-deep-literary-discovery-BY7PEDORLEaW)

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

# Initialize with performance evaluation enabled (default)
finder = LiteraryFinderGraph(enable_evaluation=True)
result = finder.process_author("Octavia Butler")

if result["success"]:
    print(result["final_report"])

    # Access performance metrics (if evaluation enabled)
    if "performance_report" in result:
        performance_summary = finder.get_performance_summary(result)
        print("\n=== PERFORMANCE SUMMARY ===")
        print(performance_summary)
else:
    print(f"Error: {result['error']}")
```

## Architecture

The Literary Finder uses three specialized AI agents orchestrated by LangGraph, each with distinct roles and capabilities:

### Agent Specializations

#### **Contextual Historian** - Biographical and Historical Research Specialist

- **Primary Role**: Comprehensive biographical fact-finding and historical context analysis
- **Capabilities**:
  - Biographical data extraction (birth/death dates, nationality, education)
  - Historical and cultural context synthesis of the author's era
  - Literary influence mapping and movement identification
  - Personal experience correlation with literary themes
- **Tools**: Web search integration, historical context analysis, pattern recognition
- **Output**: Structured `AuthorContext` with biographical summary and historical insights

#### **Literary Cartographer** - Bibliography Compilation and Reading Map Expert

- **Primary Role**: Complete bibliography compilation and strategic reading recommendations
- **Capabilities**:
  - Comprehensive book discovery using Google Books API
  - Publication chronology analysis and literary development tracking
  - Reading recommendation algorithms based on accessibility and significance
  - Multi-dimensional work categorization (genre, theme, complexity)
- **Tools**: Google Books API integration, chronological analysis, thematic categorization
- **Output**: Comprehensive `ReadingMap` with starter recommendations and thematic groups

#### **Legacy Connector** - Literary Analysis and Critical Assessment Specialist

- **Primary Role**: Literary analysis, critical reception synthesis, and influence assessment
- **Capabilities**:
  - Stylistic innovation identification and literary technique analysis
  - Recurring theme extraction and philosophical concern mapping
  - Critical reception analysis and scholarly discourse synthesis
  - Literary significance evaluation and comparative analysis
- **Tools**: Academic criticism search, thematic pattern recognition, stylistic analysis
- **Output**: Detailed `LegacyAnalysis` with innovations, themes, and critical assessment

## Technical Architecture

### Multi-Agent Orchestration Pattern

The Literary Finder implements a **supervisor-delegated multi-agent architecture** using LangGraph's stateful graph orchestration. This design pattern offers several advantages over monolithic AI systems:

**Graph-Based Workflow:**

- **Nodes:** Specialized AI agents (Contextual Historian, Literary Cartographer, Legacy Connector)
- **Edges:** Control flow paths enabling both parallel and sequential execution
- **State:** Shared memory bank tracking intermediate results and context

**Orchestration Mechanisms:**

- **Parallel Execution:** Agents run concurrently for optimal performance
- **Sequential Fallback:** Graceful degradation when dependencies require ordered execution
- **State Management:** Persistent checkpointing enables recovery and human-in-the-loop workflows

### LangGraph Integration Benefits

- **Stateful Persistence:** Unlike stateless pipelines, maintains context across agent interactions
- **Fault Tolerance:** Built-in retry mechanisms and error handling
- **Scalability:** Horizontal scaling through distributed agent execution
- **Observability:** Full transparency into agent decision-making processes

### Performance Evaluation System

The Literary Finder includes a comprehensive performance evaluation framework that assesses:

#### **System-Level Metrics**

- Execution time and throughput analysis
- Agent success/failure rates and reliability metrics
- Parallel vs sequential execution performance comparison
- Error tracking and fault tolerance assessment

#### **Agent-Level Performance**

- Individual agent execution timing and efficiency
- Tool usage patterns and optimization opportunities
- Output quality scoring based on role-specific criteria
- Data completeness and accuracy assessment

#### **Content Quality Metrics**

- **Biographical Completeness**: Scoring of biographical data coverage (dates, nationality, context)
- **Bibliography Coverage**: Assessment of reading map comprehensiveness and recommendation quality
- **Analysis Depth**: Evaluation of literary analysis quality and critical insight depth
- **Citation Quality**: Source reliability and academic rigor assessment
- **Narrative Coherence**: Final report structure and readability evaluation

#### **Automated Recommendations**

The system generates actionable optimization recommendations based on performance analysis:

- API optimization strategies for slow agents
- Error handling improvements for failed executions
- Content quality enhancement suggestions
- System configuration optimizations

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

## Performance Benchmarks

Real-world performance metrics from actual Literary Finder executions demonstrate system effectiveness:

### **System Reliability**

- **Success Rate**: 100% across all test runs
- **Agent Coordination**: All 3 specialized agents consistently successful
- **Report Generation**: 100% success rate for complete literary analysis reports
- **Average Report Length**: 13,171 characters (comprehensive content)

### **Execution Performance**

| Metric                     | Parallel Mode  | Sequential Mode |
| -------------------------- | -------------- | --------------- |
| **Success Rate**           | 100%           | 100%            |
| **Processing Time**        | 85 seconds avg | 95 seconds avg  |
| **Average Report Length**  | 13,608 chars   | 12,734 chars    |
| **Bibliography Discovery** | 21 items avg   | 0 items avg\*   |
| **Quality Score**          | 100% avg       | 75% avg         |

\*Sequential mode shows bibliography discovery issues - parallel execution recommended

### **Content Quality Assessment**

| Component                    | Success Rate | Quality Indicators                                 |
| ---------------------------- | ------------ | -------------------------------------------------- |
| **Biographical Data**        | 100%         | Comprehensive life context, historical background  |
| **Bibliography Compilation** | Variable\*\* | 0-23 book items depending on execution mode        |
| **Literary Analysis**        | 100%         | Stylistic innovations, themes, critical assessment |
| **Report Structure**         | 100%         | Complete markdown formatting with all sections     |

\*\*Bibliography compilation shows intermittent issues requiring investigation

### **Performance Insights**

#### **Execution Mode Comparison**

- **Parallel Mode**: Superior performance with 100% average quality score and robust bibliography discovery
- **Sequential Mode**: Reliable but reduced bibliography functionality (75% quality score)
- **Recommendation**: Use parallel execution for optimal results

#### **Common Performance Issues Identified**

1. **Bibliography Discovery**: Intermittent Google Books API data processing issues
2. **Biographical Data Sparsity**: Search query optimization needed for richer life context
3. **Literary Cartographer**: Occasional content extraction failures requiring data processing review

#### **Quality Score Breakdown**

- **Excellent (90%+)**: Full multi-agent coordination with comprehensive content
- **Good (70-89%)**: Successful analysis with minor component limitations
- **Target Quality**: 85%+ for production deployments

### **System Optimization Status**

Based on performance analysis, the Literary Finder demonstrates:

✅ **Strengths**

- Consistent 100% system success rate
- Robust multi-agent coordination
- Comprehensive report generation
- Real-time performance monitoring

⚠️ **Areas for Improvement**

- Bibliography compilation reliability (Google Books API integration)
- Biographical data search query enhancement
- Literary Cartographer data extraction optimization

## Troubleshooting

- **Missing API Keys**: Ensure `.env` is present and contains valid keys
- **Docker Issues**: Make sure Docker is running and ports 7860/8000 are available
- **Google Books API**: Ensure the API is enabled in your Google Cloud project
- **Web Search Not Working**: Your OpenAI API key must have web search access

## Disclaimer Notes

1. The **Literary Finder represents a functional MVP** demonstrating core multi-agent coordination principles and agentic AI capabilities. While the system successfully orchestrates specialized agents for comprehensive literary analysis, certain features remain under development, including advanced caching mechanisms, comprehensive error recovery, and production-scale optimizations.

2. **Output quality requires human review and validation** - while the system demonstrates sophisticated synthesis capabilities, generated literary analyses should be verified for accuracy, completeness, and scholarly rigor before use in academic or professional contexts.

3. **Bibliography compilation relies on Google Books API data availability and coverage**, which may not include all published works or may contain metadata inconsistencies. The current implementation prioritizes architectural demonstration and functional completeness over performance optimization.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

_The Literary Finder: Bridging the gap between readers and the vast world of literature, one author at a time._ 📚✨
