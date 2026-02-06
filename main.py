#!/usr/bin/env python3
"""
AI Operations Assistant - Main Entry Point

Supports both CLI and REST API modes
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any
from dotenv import load_dotenv

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm import LLMClient
from agents import PlannerAgent, ExecutorAgent, VerifierAgent
from tools import get_registry
from tools.github_tool import GitHubTool
from tools.weather_tool import WeatherTool
from tools.news_tool import NewsTool
from tools.exchange_tool import ExchangeRateTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIOperationsAssistant:
    """Main assistant orchestrator"""
    
    def __init__(self):
        """Initialize the AI Operations Assistant"""
        # Load environment variables
        load_dotenv()
        
        # Initialize LLM client
        try:
            self.llm_client = LLMClient()
        except ValueError as e:
            logger.error(str(e))
            raise
        
        # Initialize agents
        self.planner = PlannerAgent(self.llm_client)
        self.executor = ExecutorAgent()
        self.verifier = VerifierAgent(self.llm_client)
        
        # Register tools
        self._register_tools()
        
        logger.info("AI Operations Assistant initialized")
    
    def _register_tools(self):
        """Register all available tools"""
        registry = get_registry()
        
        tools = [
            GitHubTool(),
            WeatherTool(),
            NewsTool(),
            ExchangeRateTool()
        ]
        
        for tool in tools:
            registry.register(tool)
        
        logger.info(f"Registered {len(tools)} tools")
    
    def execute_task(self, task: str) -> Dict[str, Any]:
        """
        Execute a natural language task
        
        Args:
            task: Task description
            
        Returns:
            Execution results
        """
        logger.info(f"Executing task: {task}")
        
        try:
            # Step 1: Plan
            logger.info("Phase 1: Planning")
            plan = self.planner.plan(task)
            
            # Step 2: Execute
            logger.info("Phase 2: Execution")
            execution_results = self.executor.execute(plan)
            
            # Step 3: Verify
            logger.info("Phase 3: Verification")
            verification = self.verifier.verify(task, plan, execution_results)
            
            # Compile final response
            response = {
                "task": task,
                "status": "success" if verification["verified"] else "partial",
                "plan": plan,
                "execution": execution_results,
                "verification": verification,
                "final_answer": verification["final_answer"]
            }
            
            logger.info("Task execution complete")
            return response
            
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            return {
                "task": task,
                "status": "error",
                "error": str(e),
                "final_answer": f"I encountered an error while processing your request: {str(e)}"
            }


def run_cli(assistant: AIOperationsAssistant, task: str, verbose: bool = False):
    """
    Run in CLI mode
    
    Args:
        assistant: AI Operations Assistant instance
        task: Task to execute
        verbose: Whether to show detailed output
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("\n" + "="*80)
    print("AI OPERATIONS ASSISTANT")
    print("="*80)
    print(f"\nTask: {task}\n")
    
    result = assistant.execute_task(task)
    
    print("\n" + "-"*80)
    print("FINAL ANSWER")
    print("-"*80)
    print(result["final_answer"])
    print()
    
    if verbose:
        print("\n" + "-"*80)
        print("DETAILED RESULTS")
        print("-"*80)
        print(json.dumps(result, indent=2, default=str))
        print()
    
    print("Status:", result["status"])
    if result.get("verification"):
        print("Verified:", result["verification"].get("verified", False))
        print("Failed steps:", result["verification"].get("failed_steps", 0))
    print()


def run_api(assistant: AIOperationsAssistant, host: str = "localhost", port: int = 8000):
    """
    Run in API mode
    
    Args:
        assistant: AI Operations Assistant instance
        host: API host
        port: API port
    """
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import JSONResponse
        from pydantic import BaseModel
        import uvicorn
    except ImportError:
        logger.error("FastAPI not installed. Install with: pip install fastapi uvicorn")
        sys.exit(1)
    
    app = FastAPI(title="AI Operations Assistant API")
    
    class TaskRequest(BaseModel):
        task: str
    
    @app.post("/execute")
    async def execute_task(request: TaskRequest):
        """Execute a natural language task"""
        try:
            result = assistant.execute_task(request.task)
            return JSONResponse(content=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}
    
    @app.get("/tools")
    async def list_tools():
        """List available tools"""
        registry = get_registry()
        return {
            "tools": registry.list_tools(),
            "specs": registry.get_all_specs()
        }
    
    print("\n" + "="*80)
    print("AI OPERATIONS ASSISTANT API")
    print("="*80)
    print(f"\nServer starting on http://{host}:{port}")
    print("\nAvailable endpoints:")
    print(f"  POST http://{host}:{port}/execute - Execute a task")
    print(f"  GET  http://{host}:{port}/health - Health check")
    print(f"  GET  http://{host}:{port}/tools - List available tools")
    print("\nExample request:")
    print(f'  curl -X POST http://{host}:{port}/execute \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"task": "Find popular AI repositories on GitHub"}\'')
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(app, host=host, port=port, log_level="info")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Operations Assistant - Multi-agent AI system for task automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # CLI mode
  python main.py "Find the top 3 Python repositories on GitHub"
  python main.py --verbose "What's the weather in London?"
  
  # API mode
  python main.py --api
  python main.py --api --host 0.0.0.0 --port 8080
        """
    )
    
    parser.add_argument(
        "task",
        nargs="?",
        help="Natural language task to execute (required for CLI mode)"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run in API mode instead of CLI"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output with detailed logs"
    )
    parser.add_argument(
        "--host",
        default=os.getenv("API_HOST", "localhost"),
        help="API host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("API_PORT", "8000")),
        help="API port (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.api and not args.task:
        parser.error("task is required when not running in API mode")
    
    # Initialize assistant
    try:
        assistant = AIOperationsAssistant()
    except Exception as e:
        logger.error(f"Failed to initialize assistant: {str(e)}")
        sys.exit(1)
    
    # Run in appropriate mode
    if args.api:
        run_api(assistant, args.host, args.port)
    else:
        run_cli(assistant, args.task, args.verbose)


if __name__ == "__main__":
    main()
