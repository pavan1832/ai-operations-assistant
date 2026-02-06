"""
Verifier Agent - Validates results and ensures output quality
"""

import json
import logging
from typing import Dict, Any, List, Optional
from llm import LLMClient

logger = logging.getLogger(__name__)


class VerifierAgent:
    """Agent responsible for validating execution results and ensuring quality"""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Verifier Agent
        
        Args:
            llm_client: LLM client for reasoning
        """
        self.llm = llm_client
    
    def verify(
        self,
        task: str,
        plan: Dict[str, Any],
        execution_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify execution results meet task requirements
        
        Args:
            task: Original task
            plan: Execution plan
            execution_results: Results from Executor Agent
            
        Returns:
            Verification results with final answer
        """
        logger.info("Verifying execution results")
        
        # Check for errors
        failed_steps = [r for r in execution_results.get("results", []) if r.get("status") == "error"]
        
        if failed_steps:
            logger.warning(f"Found {len(failed_steps)} failed steps")
        
        # Analyze completeness
        completeness = self._check_completeness(task, plan, execution_results)
        
        # Generate final answer
        final_answer = self._generate_final_answer(task, execution_results, completeness)
        
        return {
            "verified": completeness["is_complete"],
            "completeness": completeness,
            "failed_steps": len(failed_steps),
            "final_answer": final_answer,
            "needs_retry": not completeness["is_complete"] and completeness.get("can_retry", False)
        }
    
    def _check_completeness(
        self,
        task: str,
        plan: Dict[str, Any],
        execution_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if execution results are complete
        
        Args:
            task: Original task
            plan: Execution plan
            execution_results: Execution results
            
        Returns:
            Completeness analysis
        """
        results = execution_results.get("results", [])
        successful_steps = [r for r in results if r.get("status") == "success"]
        total_steps = execution_results.get("total_steps", 0)
        
        # Basic completeness check
        basic_complete = len(successful_steps) == total_steps and total_steps > 0
        
        if basic_complete:
            return {
                "is_complete": True,
                "reason": "All steps completed successfully"
            }
        
        # Analyze failures
        failed_steps = [r for r in results if r.get("status") == "error"]
        
        if not failed_steps:
            return {
                "is_complete": False,
                "reason": "Some steps were skipped",
                "can_retry": False
            }
        
        # Check if failures are retryable
        retryable = any(
            "timeout" in r.get("error", "").lower() or
            "rate limit" in r.get("error", "").lower() or
            "connection" in r.get("error", "").lower()
            for r in failed_steps
        )
        
        return {
            "is_complete": False,
            "reason": f"{len(failed_steps)} steps failed",
            "failed_steps": [r.get("step") for r in failed_steps],
            "can_retry": retryable
        }
    
    def _generate_final_answer(
        self,
        task: str,
        execution_results: Dict[str, Any],
        completeness: Dict[str, Any]
    ) -> str:
        """
        Generate a natural language final answer
        
        Args:
            task: Original task
            execution_results: Execution results
            completeness: Completeness analysis
            
        Returns:
            Final answer as natural language
        """
        logger.info("Generating final answer")
        
        # Collect successful results
        successful_results = [
            r for r in execution_results.get("results", [])
            if r.get("status") == "success" and r.get("result")
        ]
        
        if not successful_results:
            return "I was unable to complete the task due to execution errors. Please check the error details and try again."
        
        # Prepare context for LLM
        results_summary = []
        for r in successful_results:
            step_desc = r.get("description", f"Step {r.get('step')}")
            result_data = r.get("result", {})
            results_summary.append({
                "step": step_desc,
                "data": result_data
            })
        
        system_prompt = """You are synthesizing execution results into a natural, helpful answer.

Guidelines:
- Be concise and clear
- Focus on the most important information
- Use natural language, not technical jargon
- Present data in an easy-to-read format
- If data is incomplete, acknowledge it gracefully"""
        
        prompt = f"""Task: {task}

Execution Results:
{json.dumps(results_summary, indent=2)}

Completeness: {completeness.get('reason', 'Complete')}

Generate a natural language answer that addresses the user's task."""
        
        try:
            answer = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2
            )
            return answer.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate final answer: {str(e)}")
            return self._create_fallback_answer(successful_results)
    
    def _create_fallback_answer(self, results: List[Dict[str, Any]]) -> str:
        """
        Create a simple fallback answer from results
        
        Args:
            results: Successful execution results
            
        Returns:
            Fallback answer
        """
        if not results:
            return "Task completed but no results available."
        
        answer_parts = ["Here are the results:\n"]
        
        for r in results:
            step_desc = r.get("description", f"Step {r.get('step')}")
            result_data = r.get("result", {})
            
            answer_parts.append(f"\n{step_desc}:")
            
            # Format based on result type
            if isinstance(result_data, dict):
                if "success" in result_data and not result_data["success"]:
                    answer_parts.append(f"  - Error: {result_data.get('error', 'Unknown error')}")
                else:
                    for key, value in result_data.items():
                        if key not in ["success", "error"]:
                            answer_parts.append(f"  - {key}: {value}")
            else:
                answer_parts.append(f"  - {result_data}")
        
        return "\n".join(answer_parts)
    
    def validate_output(self, output: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate output structure against a schema
        
        Args:
            output: Output to validate
            schema: Expected schema (optional)
            
        Returns:
            True if valid, False otherwise
        """
        if not schema:
            # Basic validation
            required_keys = ["final_answer", "verified"]
            return all(key in output for key in required_keys)
        
        # Schema-based validation (simplified)
        for key, expected_type in schema.items():
            if key not in output:
                return False
            if not isinstance(output[key], expected_type):
                return False
        
        return True
