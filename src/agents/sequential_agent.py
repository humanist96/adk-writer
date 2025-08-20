"""
SequentialAgent implementation for pipeline management
"""

from typing import List, Dict, Any, Optional
from loguru import logger


class SequentialAgent:
    """
    Sequential execution of multiple agents with memory optimization
    """
    
    def __init__(self, agents: List[Any], include_contents: str = 'all'):
        """
        Initialize SequentialAgent
        
        Args:
            agents: List of agents to execute in sequence
            include_contents: Memory management strategy ('all', 'last', 'none')
        """
        self.agents = agents
        self.include_contents = include_contents
        self.execution_history = []
        logger.info(f"SequentialAgent initialized with {len(agents)} agents, include_contents={include_contents}")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agents in sequence
        
        Args:
            input_data: Initial input for the pipeline
            
        Returns:
            Combined results from all agents
        """
        results = {}
        current_input = input_data.copy()
        
        for i, agent in enumerate(self.agents):
            agent_name = agent.name if hasattr(agent, 'name') else f"Agent_{i}"
            logger.info(f"Executing {agent_name}")
            
            try:
                # Execute agent
                if hasattr(agent, 'process'):
                    agent_result = agent.process(current_input)
                elif hasattr(agent, 'run'):
                    agent_result = agent.run(current_input)
                else:
                    raise ValueError(f"Agent {agent_name} doesn't have process or run method")
                
                # Store result based on include_contents strategy
                if self.include_contents == 'all':
                    results[agent_name] = agent_result
                    self.execution_history.append({
                        "agent": agent_name,
                        "result": agent_result
                    })
                elif self.include_contents == 'last':
                    results = {agent_name: agent_result}  # Keep only last result
                    self.execution_history = [{
                        "agent": agent_name,
                        "result": agent_result
                    }]
                elif self.include_contents == 'none':
                    # Don't store full results, only metadata
                    results[agent_name] = {
                        "completed": True,
                        "metadata": agent_result.metadata if hasattr(agent_result, 'metadata') else {}
                    }
                
                # Prepare input for next agent
                if hasattr(agent_result, 'to_dict'):
                    current_input.update(agent_result.to_dict())
                elif isinstance(agent_result, dict):
                    current_input.update(agent_result)
                else:
                    current_input["previous_result"] = agent_result
                
                logger.info(f"{agent_name} execution complete")
                
            except Exception as e:
                logger.error(f"Error executing {agent_name}: {str(e)}")
                results[agent_name] = {
                    "error": str(e),
                    "completed": False
                }
                # Decide whether to continue or stop on error
                if self._should_stop_on_error():
                    break
        
        return results
    
    def _should_stop_on_error(self) -> bool:
        """Determine if pipeline should stop on error"""
        # Can be configured based on requirements
        return True
    
    def reset(self):
        """Reset execution history"""
        self.execution_history = []
        logger.info("SequentialAgent history reset")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_history