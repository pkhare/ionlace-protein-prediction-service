"""
Protein Structure Prediction Web Service

A FastAPI-based web service that provides protein structure prediction
capabilities through an autonomous agent system.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import structlog

from protein_agent import ProteinStructureAgent
from models import (
    PredictionRequest,
    PredictionResponse,
    PredictionStatus,
    ErrorResponse,
    HealthResponse
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global agent instance
protein_agent: Optional[ProteinStructureAgent] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global protein_agent
    
    # Startup
    logger.info("🚀 Starting Protein Structure Prediction Service")
    try:
        protein_agent = ProteinStructureAgent(log_level="INFO")
        logger.info("✅ Protein Structure Agent initialized successfully")
    except Exception as e:
        logger.error("❌ Failed to initialize Protein Structure Agent", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Protein Structure Prediction Service")
    if protein_agent:
        await protein_agent.cleanup()
        logger.info("✅ Protein Structure Agent cleaned up successfully")

# Create FastAPI app
app = FastAPI(
    title="Protein Structure Prediction Service",
    description="Autonomous protein structure prediction agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with service information"""
    return HealthResponse(
        service="Protein Structure Prediction Service",
        version="1.0.0",
        status="healthy",
        description="Autonomous protein structure prediction agent"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        service="Protein Structure Prediction Service",
        version="1.0.0",
        status="healthy",
        description="Autonomous protein structure prediction agent"
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_structure(
    request: PredictionRequest,
    background_tasks: BackgroundTasks
):
    """
    Predict protein structure from amino acid sequence
    
    This endpoint initiates the autonomous agent workflow:
    1. Validates the input sequence
    2. Predicts structure using ESMFold
    3. Parses and analyzes results
    4. Generates comprehensive report
    """
    global protein_agent
    
    if not protein_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Protein Structure Agent not initialized"
        )
    
    try:
        logger.info("🔬 Starting protein structure prediction", 
                   sequence_length=len(request.sequence),
                   sequence_hash=request.sequence_hash)
        
        # Execute the agent workflow
        result = await protein_agent.execute(request.sequence)
        
        logger.info("✅ Protein structure prediction completed successfully",
                   prediction_id=result.get("prediction_id"))
        
        return PredictionResponse(
            status=PredictionStatus.COMPLETED,
            prediction_id=result.get("prediction_id"),
            sequence=request.sequence,
            sequence_hash=request.sequence_hash,
            result=result,
            message="Protein structure prediction completed successfully"
        )
        
    except Exception as e:
        logger.error("❌ Protein structure prediction failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@app.get("/predict/{prediction_id}", response_model=PredictionResponse)
async def get_prediction_status(prediction_id: str):
    """
    Get the status and results of a prediction
    
    Note: This is a simplified implementation. In a production system,
    you would store predictions in a database and track their status.
    """
    # For now, return a mock response
    # In production, implement proper prediction tracking
    return PredictionResponse(
        status=PredictionStatus.COMPLETED,
        prediction_id=prediction_id,
        sequence="MOCK_SEQUENCE",
        sequence_hash="mock_hash",
        result={"message": "This is a mock response. Implement proper prediction tracking."},
        message="Mock prediction result"
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error("❌ Unhandled exception", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc)
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
