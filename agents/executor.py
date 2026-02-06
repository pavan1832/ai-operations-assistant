"""
Executor Agent - Executes plans and calls tools
"""

import logging
from typing import Dict, Any, List
from tools import get_registry
import time

logger = logging.getLogger(__name__)


class ExecutorAgent:
    """Agent responsible for executing plans and calling tools"""
    
    def __init__(self):
        """Initialize Executor Agent"""
        self.tool_registry = get_registry()
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a plan step by step
        
        Args:
            plan: Execution plan from Planner Agent
            
        Returns:
            Execution results
        """
        logger.info("Starting plan execution")
        
        steps = plan.get("steps", [])
        results = []
        execution_context = {}  # Store results for dependent steps
        
        for step in steps:
            step_num = step.get("step_number", 0)
            logger.info(f"Executing step {step_num}: {step.get('description')}")
            
            # Check dependencies
            dependencies = step.get("depends_on", [])
            if not self._check_dependencies(dependencies, results):
                logger.warning(f"Step {step_num} dependencies not met, skipping")
                results.append({
                    "step": step_num,
                    "status": "skipped",
                    "reason": "Dependencies not met"
                })
                continue
            
            # Execute step
            step_result = self._execute_step(step, execution_context)
            results.append(step_result)
            
            # Store result for future steps
            if step_result["status"] == "success":
                execution_context[f"step_{step_num}"] = step_result["result"]
        
        # Summarize execution
        successful = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] == "error")
        
        logger.info(f"Execution complete: {successful} successful, {failed} failed")
        
        return {
            "total_steps": len(steps),
            "successful": successful,
            "failed": failed,
            "results": results,
            "execution_context": execution_context
        }
    
    def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step
        
        Args:
            step: Step to execute
            context: Execution context with previous results
            
        Returns:
            Step execution result
        """
        step_num = step.get("step_number", 0)
        tool_name = step.get("tool")
        parameters = step.get("parameters", {})
        
        # Handle steps with no tool (informational/planning steps)
        if tool_name == "none" or not tool_name:
            return {
                "step": step_num,
                "description": step.get("description"),
                "status": "success",
                "result": {"message": "Informational step completed"}
            }
        
        # Resolve parameter references to previous step results
        resolved_params = self._resolve_parameters(parameters, context)
        
        # Execute with retries
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting to execute {tool_name} (attempt {attempt + 1}/{self.max_retries})")
                
                result = self.tool_registry.execute_tool(tool_name, **resolved_params)
                
                return {
                    "step": step_num,
                    "description": step.get("description"),
                    "tool": tool_name,
                    "status": "success",
                    "result": result,
                    "attempts": attempt + 1
                }
                
            except Exception as e:
                logger.error(f"Step {step_num} attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    return {
                        "step": step_num,
                        "description": step.get("description"),
                        "tool": tool_name,
                        "status": "error",
                        "error": str(e),
                        "attempts": attempt + 1
                    }
    
    def _check_dependencies(self, dependencies: List[int], results: List[Dict[str, Any]]) -> bool:
        """
        Check if step dependencies are satisfied
        
        Args:
            dependencies: List of step numbers this step depends on
            results: Completed step results
            
        Returns:
            True if all dependencies are met
        """
        if not dependencies:
            return True
        
        completed_steps = {r.get("step") for r in results if r.get("status") == "success"}
        return all(dep in completed_steps for dep in dependencies)
    
    def _resolve_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve parameter references to context values
        
        Args:
            parameters: Parameter dictionary
            context: Execution context
            
        Returns:
            Resolved parameters
        """
        resolved = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("$step_"):
                # Reference to previous step result
                step_ref = value[1:]  # Remove $
                if step_ref in context:
                    resolved[key] = context[step_ref]
                else:
                    logger.warning(f"Could not resolve parameter reference: {value}")
                    resolved[key] = value
            else:
                resolved[key] = value
        
        return resolved
    
    def execute_single_tool(self, tool_name: str, **parameters) -> Dict[str, Any]:
        """
        Execute a single tool directly
        
        Args:
            tool_name: Name of tool to execute
            **parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            result = self.tool_registry.execute_tool(tool_name, **parameters)
            return {
                "status": "success",
                "tool": tool_name,
                "result": result
            }
        except Exception as e:
            logger.error(f"Direct tool execution failed: {str(e)}")
            return {
                "status": "error",
                "tool": tool_name,
                "error": str(e)
            }
