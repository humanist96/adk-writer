"""
LoopAgent implementation for iterative document refinement
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
import time
import json
from datetime import datetime
from loguru import logger

from .base_agents import (
    AgentResponse, 
    DraftWriterAgent, 
    CriticAgent, 
    RefinerAgent
)
from .enhanced_draft_agent import EnhancedDraftWriterAgent
from .sequential_agent import SequentialAgent
from ..config import config


@dataclass
class LoopState:
    """State management for loop iterations"""
    iteration: int = 0
    current_draft: str = ""
    current_score: float = 0.0
    history: List[Dict[str, Any]] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    exit_reason: str = ""
    final_output: str = ""
    best_score: float = 0.0  # Track best score achieved
    best_content: str = ""  # Store best content version
    score_history: List[float] = field(default_factory=list)  # Track all scores
    
    def add_iteration(self, result: Dict[str, Any]):
        """Add iteration result to history"""
        self.iteration += 1
        self.history.append({
            "iteration": self.iteration,
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
    def should_exit(self) -> bool:
        """Check if loop should exit based on conditions"""
        # Check max iterations
        if self.iteration >= config.MAX_ITERATIONS:
            self.exit_reason = f"Maximum iterations ({config.MAX_ITERATIONS}) reached"
            return True
        
        # Check timeout
        elapsed = time.time() - self.start_time
        if elapsed > config.TIMEOUT_SECONDS:
            self.exit_reason = f"Timeout ({config.TIMEOUT_SECONDS}s) exceeded"
            return True
        
        # Check quality threshold
        if self.current_score >= config.QUALITY_THRESHOLD:
            self.exit_reason = f"Quality threshold ({config.QUALITY_THRESHOLD}) achieved"
            return True
        
        return False


class LoopAgent:
    """
    Main loop controller for iterative document refinement
    Manages the writing pipeline with exit conditions
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        self.model_config = model_config
        self.state = LoopState()
        self.pipeline = None
        self.exit_conditions: List[Callable] = []
        self._setup_pipeline()
        self._setup_exit_conditions()
        logger.info("LoopAgent initialized")
    
    def _setup_pipeline(self):
        """Initialize the sequential pipeline with agents"""
        # Check if web search is enabled in config
        use_enhanced_draft = self.model_config.get('enable_web_search', False)
        
        # Create individual agents
        if use_enhanced_draft:
            draft_agent = EnhancedDraftWriterAgent(self.model_config)
            logger.info("Using EnhancedDraftWriterAgent with web search capability")
        else:
            draft_agent = DraftWriterAgent(self.model_config)
            logger.info("Using standard DraftWriterAgent")
        
        critic_agent = CriticAgent(self.model_config)
        refiner_agent = RefinerAgent(self.model_config)
        
        # Create sequential pipeline
        self.pipeline = SequentialAgent(
            agents=[draft_agent, critic_agent, refiner_agent],
            include_contents='none'  # Memory optimization
        )
        logger.info("Pipeline setup complete with 3 agents")
    
    def _setup_exit_conditions(self):
        """Setup exit condition checks"""
        self.exit_conditions = [
            self._check_quality_threshold,
            self._check_no_major_issues,
            self._check_iteration_limit,
            self._check_timeout
        ]
    
    def _check_quality_threshold(self, critique_response: AgentResponse) -> bool:
        """Check if quality threshold is met"""
        if critique_response.quality_score >= config.QUALITY_THRESHOLD:
            self.state.exit_reason = f"Quality threshold met: {critique_response.quality_score:.2f}"
            return True
        return False
    
    def _check_no_major_issues(self, critique_response: AgentResponse) -> bool:
        """Check if critic found no major issues"""
        if "No major issues found" in critique_response.content:
            self.state.exit_reason = "No major issues found by critic"
            return True
        return False
    
    def _check_iteration_limit(self, critique_response: AgentResponse) -> bool:
        """Check if maximum iterations reached"""
        if self.state.iteration >= config.MAX_ITERATIONS:
            self.state.exit_reason = f"Maximum iterations ({config.MAX_ITERATIONS}) reached"
            return True
        return False
    
    def _check_timeout(self, critique_response: AgentResponse) -> bool:
        """Check if timeout exceeded"""
        elapsed = time.time() - self.state.start_time
        if elapsed > config.TIMEOUT_SECONDS:
            self.state.exit_reason = f"Timeout ({config.TIMEOUT_SECONDS}s) exceeded"
            return True
        return False
    
    def exit_loop(self, reason: str = "Manual exit"):
        """Manually trigger loop exit"""
        self.state.exit_reason = reason
        logger.info(f"Loop exit triggered: {reason}")
        return True
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the loop agent pipeline
        
        Args:
            input_data: Initial input containing document requirements
            
        Returns:
            Final result with refined document and metadata
        """
        logger.info(f"Starting LoopAgent with document type: {input_data.get('document_type')}")
        self.state = LoopState()  # Reset state
        
        try:
            while not self.state.should_exit():
                self.state.iteration += 1
                logger.info(f"Starting iteration {self.state.iteration}")
                
                # Prepare input for pipeline
                pipeline_input = {
                    **input_data,
                    "iteration": self.state.iteration,
                    "previous_draft": self.state.current_draft,
                    "previous_score": self.state.current_score
                }
                
                # Run pipeline
                iteration_result = self._run_iteration(pipeline_input)
                
                # Update state with quality monitoring
                new_content = iteration_result.get("refined_content", "")
                new_score = iteration_result.get("quality_score", 0.0)
                
                # Track score history
                self.state.score_history.append(new_score)
                
                # Quality assurance: Check if score improved
                if new_score < self.state.current_score:
                    # Quality decreased - rollback to previous version
                    logger.warning(f"Quality decreased from {self.state.current_score:.2f} to {new_score:.2f}. Rolling back.")
                    iteration_result["rolled_back"] = True
                    iteration_result["rollback_reason"] = f"Quality decreased: {self.state.current_score:.2f} → {new_score:.2f}"
                    
                    # Keep previous content and score
                    iteration_result["refined_content"] = self.state.current_draft
                    iteration_result["quality_score"] = self.state.current_score
                else:
                    # Quality improved or maintained - update state
                    self.state.current_draft = new_content
                    self.state.current_score = new_score
                    
                    # Update best version if this is the highest score
                    if new_score > self.state.best_score:
                        self.state.best_score = new_score
                        self.state.best_content = new_content
                        logger.info(f"New best score achieved: {new_score:.2f}")
                
                self.state.add_iteration(iteration_result)
                
                # Check exit conditions
                critique_response_dict = iteration_result.get("critique_response")
                if critique_response_dict and isinstance(critique_response_dict, dict):
                    # Create a temporary AgentResponse for exit condition checking
                    from .base_agents import AgentResponse
                    temp_response = AgentResponse(
                        content=critique_response_dict.get("content", ""),
                        metadata=critique_response_dict.get("metadata", {}),
                        quality_score=critique_response_dict.get("quality_score", 0.0),
                        issues_found=critique_response_dict.get("issues_found", []),
                        suggestions=critique_response_dict.get("suggestions", [])
                    )
                    if self._should_exit(temp_response):
                        break
                
                logger.info(f"Iteration {self.state.iteration} complete. Score: {self.state.current_score:.2f}")
            
            # Finalize output - use the best version achieved
            if self.state.best_score > self.state.current_score:
                logger.info(f"Using best version (score: {self.state.best_score:.2f}) instead of current (score: {self.state.current_score:.2f})")
                self.state.final_output = self.state.best_content
                self.state.current_score = self.state.best_score
            else:
                self.state.final_output = self.state.current_draft
            
            return self._prepare_final_result()
            
        except Exception as e:
            logger.error(f"Error in LoopAgent: {str(e)}")
            raise
    
    def _run_iteration(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single iteration of the pipeline"""
        iteration_result = {}
        
        # Step 1: Generate/Update Draft
        if self.state.iteration == 1:
            # First iteration - create initial draft
            draft_response = self.pipeline.agents[0].process(input_data)
            iteration_result["draft"] = draft_response.content
            
            # Initialize best version tracking
            initial_score = draft_response.quality_score
            self.state.best_score = initial_score
            self.state.best_content = draft_response.content
            self.state.current_score = initial_score
            self.state.current_draft = draft_response.content
            
            # Store web search results if available
            if hasattr(draft_response, 'web_search_results') and draft_response.web_search_results:
                self.web_search_results = draft_response.web_search_results
                iteration_result["web_search_results"] = draft_response.web_search_results
                logger.info(f"Stored web search results with {len(draft_response.web_search_results.get('relevant_information', []))} sources")
                logger.debug(f"Web search results keys: {draft_response.web_search_results.keys()}")
            else:
                logger.warning(f"No web search results found in draft response. Has attribute: {hasattr(draft_response, 'web_search_results')}, Value: {getattr(draft_response, 'web_search_results', None)}")
        else:
            # Subsequent iterations - use refined content from previous iteration
            iteration_result["draft"] = input_data.get("previous_draft", "")
        
        # Step 2: Critique
        critique_input = {
            **input_data,
            "draft": iteration_result["draft"]
        }
        critique_response = self.pipeline.agents[1].process(critique_input)
        iteration_result["critique"] = critique_response.content
        # Convert AgentResponse to dict for JSON serialization
        iteration_result["critique_response"] = critique_response.to_dict() if hasattr(critique_response, 'to_dict') else str(critique_response)
        iteration_result["quality_score"] = critique_response.quality_score
        iteration_result["issues"] = critique_response.issues_found
        iteration_result["suggestions"] = critique_response.suggestions
        
        # Step 3: Refine (if issues found)
        if "No major issues found" not in critique_response.content:
            refine_input = {
                **input_data,
                "draft": iteration_result["draft"],
                "critique": critique_response.content,
                "previous_score": critique_response.quality_score
            }
            refine_response = self.pipeline.agents[2].process(refine_input)
            iteration_result["refined_content"] = refine_response.content
            iteration_result["quality_score"] = refine_response.quality_score
        else:
            iteration_result["refined_content"] = iteration_result["draft"]
        
        return iteration_result
    
    def _should_exit(self, critique_response: AgentResponse) -> bool:
        """Check all exit conditions"""
        for condition_check in self.exit_conditions:
            if condition_check(critique_response):
                return True
        return False
    
    def _prepare_final_result(self) -> Dict[str, Any]:
        """Prepare the final result with all metadata"""
        result = {
            "success": True,
            "final_document": self.state.final_output,
            "quality_score": self.state.current_score,
            "iterations": self.state.iteration,
            "exit_reason": self.state.exit_reason,
            "total_time": time.time() - self.state.start_time,
            "history": self.state.history,
            "quality_monitoring": {
                "initial_score": self.state.score_history[0] if self.state.score_history else 0.7,
                "final_score": self.state.current_score,
                "best_score": self.state.best_score,
                "score_progression": self.state.score_history,
                "quality_improved": self.state.current_score > (self.state.score_history[0] if self.state.score_history else 0.7),
                "improvement_percentage": ((self.state.current_score - (self.state.score_history[0] if self.state.score_history else 0.7)) * 100) if self.state.score_history else 0
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "config": {
                    "max_iterations": config.MAX_ITERATIONS,
                    "quality_threshold": config.QUALITY_THRESHOLD,
                    "timeout": config.TIMEOUT_SECONDS
                },
                "quality_assurance": {
                    "rollback_enabled": True,
                    "minimum_improvement": 0.01,
                    "best_version_tracking": True
                }
            }
        }
        
        # Add web search results if available
        if hasattr(self, 'web_search_results') and self.web_search_results:
            result['web_search_results'] = self.web_search_results
            logger.info(f"Added web search results to final result: {len(self.web_search_results.get('relevant_information', []))} sources")
        else:
            logger.warning(f"No web search results to add to final result. Has attribute: {hasattr(self, 'web_search_results')}, Value: {getattr(self, 'web_search_results', None)}")
        
        return result
    
    def get_state(self) -> Dict[str, Any]:
        """Get current loop state"""
        return {
            "iteration": self.state.iteration,
            "current_score": self.state.current_score,
            "elapsed_time": time.time() - self.state.start_time,
            "exit_reason": self.state.exit_reason
        }