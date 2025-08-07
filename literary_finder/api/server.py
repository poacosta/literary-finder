"""FastAPI server for the Literary Finder system."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import time
from langsmith import traceable
from ..orchestration import LiteraryFinderGraph
from ..models import APIResponse
from ..config import LangSmithConfig
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="The Literary Finder",
    description="A Multi-Agent System for Deep Literary Discovery",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

literary_graph: Optional[LiteraryFinderGraph] = None


class AuthorRequest(BaseModel):
    """Request model for author analysis."""
    author_name: str
    llm_provider: Optional[str] = "openai"
    model_name: Optional[str] = None
    enable_parallel: Optional[bool] = True


class AuthorResponse(BaseModel):
    """Response model for author analysis."""
    success: bool
    author_name: str
    final_report: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    errors: list[str] = []


@app.on_event("startup")
async def startup_event():
    """Initialize the Literary Finder graph on startup."""
    global literary_graph

    try:
        # Initialize LangSmith tracing
        LangSmithConfig.setup_tracing("literary-finder-api")
        
        if LangSmithConfig.is_enabled():
            logger.info("🔍 LangSmith tracing enabled for API")
        else:
            logger.info("📊 LangSmith tracing disabled (API key not configured)")
        
        # Check for required environment variables
        required_vars = ["OPENAI_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            logger.warning(f"Missing environment variables: {missing_vars}")
            logger.warning("Some features may be limited or unavailable")

        literary_graph = LiteraryFinderGraph(
            llm_provider="openai",
            enable_parallel=True
        )

        logger.info("Literary Finder system initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize Literary Finder: {e}")
        literary_graph = None


@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "service": "The Literary Finder",
        "description": "A Multi-Agent System for Deep Literary Discovery",
        "version": "0.1.0",
        "status": "ready" if literary_graph else "error",
        "endpoints": {
            "analyze": "/analyze",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if literary_graph else "unhealthy",
        "timestamp": time.time(),
        "graph_initialized": literary_graph is not None
    }


@app.post("/analyze", response_model=AuthorResponse)
@traceable(name="api_analyze_author")
async def analyze_author(request: AuthorRequest):
    """Analyze an author and generate a comprehensive report."""

    if not literary_graph:
        raise HTTPException(
            status_code=503,
            detail="Literary Finder system not initialized. Check logs for configuration issues."
        )

    if not request.author_name or not request.author_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Author name is required and cannot be empty"
        )

    start_time = time.time()

    try:
        logger.info(f"Starting analysis for author: {request.author_name}")

        graph = literary_graph
        if (request.llm_provider != "openai" or
                request.model_name or
                request.enable_parallel != True):
            logger.info(f"Creating custom graph with settings: {request.llm_provider}, {request.model_name}")
            graph = LiteraryFinderGraph(
                llm_provider=request.llm_provider,
                model_name=request.model_name,
                enable_parallel=request.enable_parallel
            )

        result = graph.process_author(request.author_name.strip())

        processing_time = time.time() - start_time

        if result["success"]:
            logger.info(f"Analysis completed for {request.author_name} in {processing_time:.2f}s")

            return AuthorResponse(
                success=True,
                author_name=request.author_name,
                final_report=result.get("final_report"),
                processing_time_seconds=round(processing_time, 2),
                errors=result.get("errors", [])
            )
        else:
            logger.error(f"Analysis failed for {request.author_name}: {result.get('error')}")

            return AuthorResponse(
                success=False,
                author_name=request.author_name,
                processing_time_seconds=round(processing_time, 2),
                errors=[result.get("error", "Unknown error occurred")]
            )

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Unexpected error analyzing {request.author_name}: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during analysis: {str(e)}"
        )


@app.get("/analyze/{author_name}")
async def analyze_author_get(author_name: str):
    """GET endpoint for analyzing an author (simpler interface)."""

    request = AuthorRequest(author_name=author_name)
    return await analyze_author(request)


if __name__ == "__main__":
    import uvicorn

    from dotenv import load_dotenv

    load_dotenv()

    uvicorn.run(
        "literary_finder.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
