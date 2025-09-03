"""
Protein Structure Prediction Agent
IONLACE Technical Interview Assignment

Refactored agent module for web service integration
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

from esmfold_client import ESMFoldClient, ESMFoldConfig
from models import ProteinStructure, AnalysisResult, PredictionReport

# Import Bio for protein structure parsing
try:
    from Bio import PDB
    from Bio.PDB import PDBParser, PPBuilder
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False

class StepStatus(Enum):
    """Status of execution steps"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"

class DecisionType(Enum):
    """Agent decision types"""
    CONTINUE = "continue"
    RETRY = "retry"
    FALLBACK = "fallback"
    ABORT = "abort"
    COMPLETE = "complete"

@dataclass
class ExecutionStep:
    """Represents a single step in the agent's execution plan"""
    name: str
    description: str
    function_name: str
    dependencies: List[str] = field(default_factory=list)
    max_retries: int = 3
    timeout_seconds: int = 30

@dataclass
class StepResult:
    """Result of executing a single step"""
    step_name: str
    status: StepStatus
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    attempt_number: int = 1

@dataclass
class Decision:
    """Agent's decision after observing a step result"""
    action: DecisionType
    reason: str
    next_step: Optional[str] = None
    retry_delay: float = 1.0

@dataclass
class AgentState:
    """Maintains agent's execution state"""
    sequence: str = ""
    sequence_hash: str = ""
    prediction_id: str = ""
    current_step_index: int = 0
    execution_plan: List[ExecutionStep] = field(default_factory=list)
    results: Dict[str, StepResult] = field(default_factory=dict)
    execution_log: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)

    def is_complete(self) -> bool:
        """Check if all steps are completed successfully"""
        return self.current_step_index >= len(self.execution_plan)

    def get_current_step(self) -> Optional[ExecutionStep]:
        """Get the current step to execute"""
        if self.current_step_index < len(self.execution_plan):
            return self.execution_plan[self.current_step_index]
        return None

    def mark_step_complete(self):
        """Move to next step"""
        self.current_step_index += 1

class ProteinStructureAgent:
    """
    Autonomous agent for protein structure prediction and analysis.
    
    Implements think/plan/act/observe cycle to:
    1. Validate amino acid sequences
    2. Call structure prediction APIs (ESMFold)
    3. Parse and analyze results
    4. Generate comprehensive reports
    """

    def __init__(self, log_level: str = "INFO"):
        self.state = AgentState()
        self.logger = self._setup_logging(log_level)
        self.esmfold_client = None

        # Step functions mapping
        self.step_functions = {
            "validate_sequence": self._validate_sequence,
            "predict_structure": self._predict_structure,
            "parse_structure": self._parse_structure,
            "calculate_metrics": self._calculate_metrics,
            "generate_report": self._generate_report
        }

    def _setup_logging(self, level: str) -> logging.Logger:
        """Setup logging for the agent"""
        logger = logging.getLogger("ProteinAgent")
        
        # Clear existing handlers
        logger.handlers.clear()
        logger.propagate = False
        
        logger.setLevel(getattr(logging, level))
        
        # Add handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    async def execute(self, sequence: str) -> Dict[str, Any]:
        """
        Main orchestrator - executes the complete think/plan/act/observe cycle
        
        Args:
            sequence: Amino acid sequence to analyze
            
        Returns:
            Final report with structure prediction and analysis
        """
        self.logger.info("🚀 Starting Protein Structure Prediction Agent")
        
        # Initialize state
        self.state.sequence = sequence.strip().upper()
        self.state.sequence_hash = hashlib.md5(sequence.encode()).hexdigest()[:8]
        self.state.prediction_id = str(uuid.uuid4())
        
        # THINK: Analyze the task
        thought = self.think()
        self.logger.info(f"🤔 THINK: {thought}")
        
        # PLAN: Create execution strategy
        execution_plan = self.plan()
        self.state.execution_plan = execution_plan
        self.logger.info(f"📋 PLAN: {len(execution_plan)} steps planned")
        
        for i, step in enumerate(execution_plan, 1):
            self.logger.info(f"   Step {i}: {step.description}")
        
        # Main execution loop
        while not self.state.is_complete():
            current_step = self.state.get_current_step()
            if not current_step:
                break
                
            self.logger.info(f"⚡ ACT: {current_step.description}...")
            
            # Execute step with timing
            start_time = time.time()
            result = await self.act(current_step)
            result.execution_time = time.time() - start_time
            
            # Store result
            self.state.results[current_step.name] = result
            
            # OBSERVE: Evaluate result and decide next action
            decision = self.observe(result)
            self.logger.info(f"👁️ OBSERVE: {decision.reason}")
            
            # Handle decision
            if decision.action == DecisionType.CONTINUE:
                self.state.mark_step_complete()
            elif decision.action == DecisionType.RETRY:
                self.logger.info(f"🔄 Retrying in {decision.retry_delay}s...")
                await asyncio.sleep(decision.retry_delay)
            elif decision.action == DecisionType.FALLBACK:
                self.logger.warning("⚠️ Attempting fallback strategy")
                # Implement fallback logic here
                self.state.mark_step_complete()
            elif decision.action == DecisionType.ABORT:
                self.logger.error("❌ Aborting execution")
                break
            elif decision.action == DecisionType.COMPLETE:
                self.logger.info("✅ Execution completed")
                break
        
        # Generate final report
        final_report = await self._generate_final_report()
        return final_report

    def think(self) -> str:
        """Analyze the current task and context"""
        sequence_length = len(self.state.sequence)
        
        if sequence_length > 400:
            return f"Sequence length {sequence_length} exceeds ESMFold limit of 400. Will need to truncate."
        elif sequence_length > 200:
            return f"Long sequence ({sequence_length} residues). Prediction may take longer and use more memory."
        else:
            return f"Standard sequence length ({sequence_length} residues). Proceeding with normal workflow."

    def plan(self) -> List[ExecutionStep]:
        """Create execution plan based on current state"""
        return [
            ExecutionStep(
                name="validate_sequence",
                description="Validate amino acid sequence format and content",
                function_name="validate_sequence",
                timeout_seconds=10
            ),
            ExecutionStep(
                name="predict_structure",
                description="Predict protein structure using ESMFold",
                function_name="predict_structure",
                dependencies=["validate_sequence"],
                timeout_seconds=300
            ),
            ExecutionStep(
                name="parse_structure",
                description="Parse and validate predicted structure",
                function_name="parse_structure",
                dependencies=["predict_structure"],
                timeout_seconds=60
            ),
            ExecutionStep(
                name="calculate_metrics",
                description="Calculate structural and quality metrics",
                function_name="calculate_metrics",
                dependencies=["parse_structure"],
                timeout_seconds=30
            ),
            ExecutionStep(
                name="generate_report",
                description="Generate comprehensive analysis report",
                function_name="generate_report",
                dependencies=["calculate_metrics"],
                timeout_seconds=30
            )
        ]

    async def act(self, step: ExecutionStep) -> StepResult:
        """Execute a single step"""
        try:
            if step.function_name in self.step_functions:
                result = await self.step_functions[step.function_name]()
                return StepResult(
                    step_name=step.name,
                    status=StepStatus.SUCCESS,
                    data=result,
                    execution_time=0.0
                )
            else:
                return StepResult(
                    step_name=step.name,
                    status=StepStatus.FAILED,
                    error=f"Unknown function: {step.function_name}"
                )
        except Exception as e:
            self.logger.error(f"Step {step.name} failed: {str(e)}")
            return StepResult(
                step_name=step.name,
                status=StepStatus.FAILED,
                error=str(e)
            )

    def observe(self, result: StepResult) -> Decision:
        """Evaluate step result and decide next action"""
        if result.status == StepStatus.SUCCESS:
            return Decision(
                action=DecisionType.CONTINUE,
                reason=f"Step {result.step_name} completed successfully"
            )
        else:
            # For now, just continue on failure
            # In production, implement retry logic
            return Decision(
                action=DecisionType.CONTINUE,
                reason=f"Step {result.step_name} failed, but continuing"
            )

    async def _validate_sequence(self) -> Dict[str, Any]:
        """Validate the input amino acid sequence"""
        sequence = self.state.sequence
        
        # Basic validation
        if not sequence:
            raise ValueError("Sequence cannot be empty")
        
        if len(sequence) > 400:
            raise ValueError("Sequence length exceeds ESMFold limit of 400 residues")
        
        # Validate amino acid characters
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        invalid_chars = set(sequence) - valid_aa
        
        if invalid_chars:
            raise ValueError(f"Invalid amino acid characters: {invalid_chars}")
        
        return {
            "sequence": sequence,
            "length": len(sequence),
            "valid": True,
            "validation_notes": "Sequence passed all validation checks"
        }

    async def _predict_structure(self) -> Dict[str, Any]:
        """Predict protein structure using ESMFold"""
        if not self.esmfold_client:
            config = ESMFoldConfig()
            self.esmfold_client = ESMFoldClient(config)
        
        try:
            result = await self.esmfold_client.predict_structure(self.state.sequence)
            
            if result.success:
                return {
                    "pdb_content": result.pdb_content,
                    "confidence_scores": result.confidence_scores,
                    "plddt_scores": result.plddt_scores,
                    "method_used": result.method_used,
                    "prediction_time": result.prediction_time
                }
            else:
                raise ValueError(f"Structure prediction failed: {result.error_message}")
                
        except Exception as e:
            self.logger.error(f"Structure prediction error: {str(e)}")
            raise

    async def _parse_structure(self) -> Dict[str, Any]:
        """Parse the predicted protein structure"""
        # Get structure data from previous step
        predict_result = self.state.results.get("predict_structure")
        if not predict_result or predict_result.status != StepStatus.SUCCESS:
            raise ValueError("Structure prediction step did not complete successfully")
        
        structure_data = predict_result.data
        if not structure_data or "pdb_content" not in structure_data:
            raise ValueError("No structure data available for parsing")
        
        pdb_content = structure_data["pdb_content"]
        
        # Basic PDB parsing
        lines = pdb_content.strip().split('\n')
        atoms = []
        residues = set()
        
        for line in lines:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                # Parse atom line
                try:
                    atom_name = line[12:16].strip()
                    res_name = line[17:20].strip()
                    res_seq = int(line[22:26])
                    residues.add((res_name, res_seq))
                    atoms.append(line)
                except (ValueError, IndexError):
                    continue
        
        return {
            "total_atoms": len(atoms),
            "total_residues": len(residues),
            "pdb_content": pdb_content,
            "parsing_method": "basic_pdb_parser"
        }

    async def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate structural and quality metrics"""
        parse_result = self.state.results.get("parse_structure")
        predict_result = self.state.results.get("predict_structure")
        
        if not parse_result or parse_result.status != StepStatus.SUCCESS:
            raise ValueError("Structure parsing step did not complete successfully")
        
        structure_data = parse_result.data
        prediction_data = predict_result.data if predict_result else {}
        
        if not structure_data:
            raise ValueError("No structure data available for metrics calculation")
        
        metrics = {
            "total_atoms": structure_data.get("total_atoms", 0),
            "total_residues": structure_data.get("total_residues", 0),
            "sequence_length": len(self.state.sequence),
            "prediction_method": prediction_data.get("method_used", "unknown") if prediction_data else "unknown",
            "confidence_score": prediction_data.get("confidence_scores", {}).get("overall", 0.0) if prediction_data else 0.0,
            "average_plddt": 0.0
        }
        
        # Calculate average pLDDT if available
        plddt_scores = prediction_data.get("plddt_scores", []) if prediction_data else []
        if plddt_scores:
            metrics["average_plddt"] = sum(plddt_scores) / len(plddt_scores)
        
        return metrics

    async def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        # Collect all step results
        all_results = {}
        for step_name, result in self.state.results.items():
            all_results[step_name] = {
                "status": result.status.value,
                "data": result.data,
                "execution_time": result.execution_time,
                "error": result.error
            }
        
        # Calculate total execution time
        total_time = (datetime.now() - self.state.start_time).total_seconds()
        
        return {
            "prediction_id": self.state.prediction_id,
            "sequence": self.state.sequence,
            "sequence_hash": self.state.sequence_hash,
            "execution_summary": {
                "total_steps": len(self.state.execution_plan),
                "completed_steps": len(self.state.results),
                "total_execution_time": total_time,
                "start_time": self.state.start_time.isoformat(),
                "end_time": datetime.now().isoformat()
            },
            "step_results": all_results,
            "final_metrics": all_results.get("calculate_metrics", {}).get("data", {}),
            "structure_data": all_results.get("parse_structure", {}).get("data", {})
        }

    async def _generate_final_report(self) -> Dict[str, Any]:
        """Generate the final report in the expected format"""
        report = await self._generate_report()
        
        # Add timestamp
        report["timestamp"] = datetime.now().isoformat()
        
        return report

    async def cleanup(self):
        """Clean up resources"""
        if self.esmfold_client:
            await self.esmfold_client.cleanup()
            self.esmfold_client = None
        
        self.logger.info("🧹 Agent cleanup completed")
