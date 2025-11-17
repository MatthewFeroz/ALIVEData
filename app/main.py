"""
ALIVE Data Web Application - FastAPI Main Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from app.api import routes
from app.core.config import settings

# Create necessary directories
Path("uploads").mkdir(exist_ok=True)
Path("static/uploads").mkdir(parents=True, exist_ok=True)
Path("docs/sessions").mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="ALIVE Data API",
    description="API for capturing screenshots, performing OCR, and generating documentation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, prefix="/api")

# Mount static files for serving uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ALIVE Data API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

