"""
Simple Enhanced SciRAG API server.
This version works without complex dependencies.
"""

import sys
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add the scirag directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import enhanced processing components directly
from scirag.enhanced_processing.mathematical_processor import MathematicalProcessor
from scirag.enhanced_processing.content_classifier import ContentClassifier
from scirag.enhanced_processing.enhanced_chunker import EnhancedChunker
from scirag.enhanced_processing.asset_processor import AssetProcessor
from scirag.enhanced_processing.glossary_extractor import GlossaryExtractor

# Create FastAPI app
app = FastAPI(
    title="Enhanced SciRAG API",
    description="Enhanced SciRAG with RAGBook Integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
mathematical_processor = MathematicalProcessor()
content_classifier = ContentClassifier()
enhanced_chunker = EnhancedChunker()
asset_processor = AssetProcessor()
glossary_extractor = GlossaryExtractor()

# Request/Response Models
class ProcessDocumentRequest(BaseModel):
    """Process document request model."""
    content: str = Field(..., description="Document content to process")
    content_type: Optional[str] = Field("auto", description="Content type (auto, equation, prose, figure, table)")
    source_id: Optional[str] = Field("unknown", description="Source document ID")

class ProcessDocumentResponse(BaseModel):
    """Process document response model."""
    content_type: str = Field(..., description="Detected content type")
    enhanced_chunks: List[Dict[str, Any]] = Field(..., description="Generated enhanced chunks")
    mathematical_content: Optional[Dict[str, Any]] = Field(None, description="Mathematical processing results")
    assets: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted assets")
    glossary_terms: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted glossary terms")
    processing_time: float = Field(..., description="Processing time in seconds")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Enhanced SciRAG API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    import datetime
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.datetime.now().isoformat()
    )

@app.post("/api/v2/process-document", response_model=ProcessDocumentResponse)
async def process_document(request: ProcessDocumentRequest):
    """Process a document with enhanced SciRAG capabilities."""
    import time
    start_time = time.time()
    
    try:
        # Classify content type
        if request.content_type == "auto":
            content_type = content_classifier.classify_content(request.content)
        else:
            content_type = request.content_type
        
        # Generate enhanced chunks
        chunks = enhanced_chunker.chunk_document(request.content, request.source_id)
        
        # Convert chunks to dictionaries
        enhanced_chunks = []
        mathematical_content = None
        assets = []
        glossary_terms = []
        
        for chunk in chunks:
            chunk_dict = {
                "content": chunk.content,
                "content_type": chunk.content_type,
                "source_id": chunk.source_id,
                "chunk_id": chunk.chunk_id
            }
            
            # Add mathematical content if present
            if hasattr(chunk, 'mathematical_content') and chunk.mathematical_content:
                mathematical_content = {
                    "equation_tex": chunk.mathematical_content.equation_tex,
                    "math_norm": chunk.mathematical_content.math_norm,
                    "equation_type": chunk.mathematical_content.equation_type,
                    "complexity_score": chunk.mathematical_content.complexity_score
                }
            
            # Add assets if present
            if hasattr(chunk, 'assets') and chunk.assets:
                for asset in chunk.assets:
                    assets.append({
                        "asset_type": asset.asset_type,
                        "content": asset.content,
                        "metadata": asset.metadata
                    })
            
            # Add glossary terms if present
            if hasattr(chunk, 'glossary_terms') and chunk.glossary_terms:
                for term in chunk.glossary_terms:
                    glossary_terms.append({
                        "term": term.term,
                        "definition": term.definition,
                        "context": term.context
                    })
            
            enhanced_chunks.append(chunk_dict)
        
        processing_time = time.time() - start_time
        
        return ProcessDocumentResponse(
            content_type=content_type,
            enhanced_chunks=enhanced_chunks,
            mathematical_content=mathematical_content,
            assets=assets,
            glossary_terms=glossary_terms,
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/api/v2/process-equation")
async def process_equation(equation: str):
    """Process a mathematical equation."""
    try:
        result = mathematical_processor.process_equation(equation)
        return {
            "equation": equation,
            "result": result,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Equation processing error: {str(e)}")

@app.post("/api/v2/classify-content")
async def classify_content(content: str):
    """Classify content type."""
    try:
        content_type = content_classifier.classify_content(content)
        return {
            "content": content,
            "content_type": content_type,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content classification error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
