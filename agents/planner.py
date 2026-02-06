"""
Planner Agent - Analyzes tasks and creates execution plans
"""

import json
import logging
from typing import Dict, Any, List
from llm import LLMClient
from tools import get_registry

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Agent responsible for analyzing tasks and creating execution plans"""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Planner Agent
        
        Args:
            llm_client: LLM client for reasoning
        """
        self.llm = llm_client
        self.tool_registry = get_registry()
    
    def plan(self, task: str) -> Dict[str, Any]:
        """
        Create an execution plan for a given task
        
        Args:
            task: Natural language task description
            
        Returns:
            Execution plan with steps and tools
        """
        logger.info(f"Planning task: {task}")
        
        # Get available tools
        available_tools = self.tool_registry.get_all_specs()
        
        # Create planning prompt
        system_prompt = """You are a planning agent that breaks down tasks into executable steps.
Your job is to analyze the user's task and create a detailed execution plan.

Guidelines:
- Break complex tasks into simple, sequential steps
- Identify which tools are needed for each step
- Be specific about tool parameters
- Consider dependencies between steps
- Plan for error handling

Output a JSON object with this structure:
{
  "task_analysis": "Brief analysis of what needs to be done",
  "steps": [
    {
      "step_number": 1,
      "description": "What this step does",
      "tool": "tool_name",
      "parameters": {"param1": "value1"},
      "depends_on": []
    }
  ],
  "required_tools": ["tool1", "tool2"]
}"""
        
        prompt = f"""Task: {task}

Available tools:
{json.dumps(available_tools, indent=2)}

Create a detailed execution plan for this task."""
        
        try:
            plan_data = self.llm.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            # Validate plan structure
            if not self._validate_plan(plan_data):
                logger.warning("Generated plan failed validation, attempting to fix")
                plan_data = self._fix_plan(plan_data, task)
            
            logger.info(f"Created plan with {len(plan_data.get('steps', []))} steps")
            return plan_data
            
        except Exception as e:
            logger.error(f"Planning failed: {str(e)}")
            # Return a minimal fallback plan
            return self._create_fallback_plan(task)
    
    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Validate plan structure
        
        Args:
            plan: Plan to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ["task_analysis", "steps", "required_tools"]
        if not all(key in plan for key in required_keys):
            return False
        
        if not isinstance(plan["steps"], list) or len(plan["steps"]) == 0:
            return False
        
        # Validate each step
        for step in plan["steps"]:
            required_step_keys = ["step_number", "description", "tool", "parameters"]
            if not all(key in step for key in required_step_keys):
                return False
            
            # Check if tool exists
            tool_name = step["tool"]
            if tool_name != "none" and not self.tool_registry.get(tool_name):
                logger.warning(f"Plan references unknown tool: {tool_name}")
                return False
        
        return True
    
    def _fix_plan(self, plan: Dict[str, Any], task: str) -> Dict[str, Any]:
        """
        Attempt to fix an invalid plan
        
        Args:
            plan: Invalid plan
            task: Original task
            
        Returns:
            Fixed plan
        """
        # Add missing keys with defaults
        if "task_analysis" not in plan:
            plan["task_analysis"] = f"Execute task: {task}"
        
        if "steps" not in plan or not plan["steps"]:
            plan["steps"] = [{
                "step_number": 1,
                "description": task,
                "tool": "none",
                "parameters": {},
                "depends_on": []
            }]
        
        if "required_tools" not in plan:
            plan["required_tools"] = []
        
        # Fix steps
        for i, step in enumerate(plan["steps"]):
            if "step_number" not in step:
                step["step_number"] = i + 1
            if "description" not in step:
                step["description"] = f"Step {i + 1}"
            if "tool" not in step:
                step["tool"] = "none"
            if "parameters" not in step:
                step["parameters"] = {}
            if "depends_on" not in step:
                step["depends_on"] = []
        
        return plan
    
    def _create_fallback_plan(self, task: str) -> Dict[str, Any]:
        """
        Create a simple fallback plan when planning fails
        
        Args:
            task: Task description
            
        Returns:
            Fallback plan
        """
        return {
            "task_analysis": f"Simple execution of: {task}",
            "steps": [
                {
                    "step_number": 1,
                    "description": task,
                    "tool": "none",
                    "parameters": {},
                    "depends_on": []
                }
            ],
            "required_tools": []
        }
    
    def refine_plan(self, plan: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Refine an existing plan based on feedback
        
        Args:
            plan: Current plan
            feedback: Feedback from execution or verification
            
        Returns:
            Refined plan
        """
        logger.info("Refining plan based on feedback")
        
        prompt = f"""Original plan:
{json.dumps(plan, indent=2)}

Feedback: {feedback}

Refine the plan to address this feedback. Maintain the same JSON structure."""
        
        system_prompt = "You are refining an execution plan based on feedback. Keep successful steps and modify or add steps as needed."
        
        try:
            refined_plan = self.llm.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            if self._validate_plan(refined_plan):
                return refined_plan
            else:
                logger.warning("Refined plan failed validation, returning original")
                return plan
                
        except Exception as e:
            logger.error(f"Plan refinement failed: {str(e)}")
            return plan
