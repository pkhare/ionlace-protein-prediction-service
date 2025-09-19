"""
Pydantic models for the Protein Structure Prediction API
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator
import hashlib

class PredictionStatus(str, Enum):
    """Status of a protein structure prediction"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PredictionRequest(BaseModel):
    """Request model for protein structure prediction"""
    sequence: str = Field(
        ...,
        description="Amino acid sequence to predict structure for",
        min_length=1,
        max_length=400,  # ESMFold limit
        example="MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    )
    
    @validator('sequence')
    def validate_sequence(cls, v):
        """Validate amino acid sequence"""
        if not v:
            raise ValueError("Sequence cannot be empty")
        
        # Convert to uppercase and validate characters
        v = v.upper().strip()
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        
        invalid_chars = set(v) - valid_aa
        if invalid_chars:
            raise ValueError(f"Invalid amino acid characters: {invalid_chars}")
        
        return v
    
    @property
    def sequence_hash(self) -> str:
        """Generate a hash of the sequence for tracking"""
        return hashlib.md5(self.sequence.encode()).hexdigest()[:8]

class PredictionResponse(BaseModel):
    """Response model for protein structure prediction"""
    status: PredictionStatus
    prediction_id: str
    sequence: str
    sequence_hash: str
    result: Dict[str, Any]
    message: str
    timestamp: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
    timestamp: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response model"""
    service: str
    version: str
    status: str
    description: str
    timestamp: Optional[str] = None

class ProteinStructure(BaseModel):
    """Protein structure model"""
    pdb_content: str
    confidence_score: Optional[float] = None
    plddt_scores: Optional[List[float]] = None
    method_used: str
    prediction_time: float

class AnalysisResult(BaseModel):
    """Protein analysis result model"""
    total_atoms: int
    total_residues: int
    sequence_length: int
    secondary_structure: Optional[Dict[str, Any]] = None
    structural_metrics: Optional[Dict[str, Any]] = None
    method_used: str

class PredictionReport(BaseModel):
    """Complete prediction report model"""
    prediction_id: str
    sequence: str
    sequence_hash: str
    structure: ProteinStructure
    analysis: AnalysisResult
    execution_summary: Dict[str, Any]
    timestamp: str
