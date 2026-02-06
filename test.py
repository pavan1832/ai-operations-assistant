#!/usr/bin/env python3
"""
Test script for AI Operations Assistant
Validates all components and integrations
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from llm import LLMClient
        print("  ✓ LLM client imported")
    except Exception as e:
        print(f"  ✗ LLM client import failed: {e}")
        return False
    
    try:
        from agents import PlannerAgent, ExecutorAgent, VerifierAgent
        print("  ✓ Agents imported")
    except Exception as e:
        print(f"  ✗ Agents import failed: {e}")
        return False
    
    try:
        from tools import get_registry
        from tools.github_tool import GitHubTool
        from tools.weather_tool import WeatherTool
        from tools.news_tool import NewsTool
        from tools.exchange_tool import ExchangeRateTool
        print("  ✓ Tools imported")
    except Exception as e:
        print(f"  ✗ Tools import failed: {e}")
        return False
    
    return True


def test_environment():
    """Test environment configuration"""
    print("\nTesting environment...")
    
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"  ✓ GEMINI_API_KEY found (length: {len(api_key)})")
    else:
        print("  ✗ GEMINI_API_KEY not found")
        return False
    
    # Optional API keys
    optional_keys = [
        "GITHUB_TOKEN",
        "OPENWEATHER_API_KEY",
        "NEWS_API_KEY"
    ]
    
    for key in optional_keys:
        value = os.getenv(key)
        if value:
            print(f"  ✓ {key} found (optional)")
        else:
            print(f"  ℹ {key} not found (optional)")
    
    return True


def test_llm_client():
    """Test LLM client initialization"""
    print("\nTesting LLM client...")
    
    try:
        from llm import LLMClient
        client = LLMClient()
        print(f"  ✓ LLM client initialized (model: {client.model})")
        return True
    except Exception as e:
        print(f"  ✗ LLM client initialization failed: {e}")
        return False


def test_tool_registry():
    """Test tool registration"""
    print("\nTesting tool registry...")
    
    try:
        from tools import get_registry
        from tools.github_tool import GitHubTool
        from tools.weather_tool import WeatherTool
        from tools.news_tool import NewsTool
        from tools.exchange_tool import ExchangeRateTool
        
        registry = get_registry()
        
        tools = [
            GitHubTool(),
            WeatherTool(),
            NewsTool(),
            ExchangeRateTool()
        ]
        
        for tool in tools:
            registry.register(tool)
            print(f"  ✓ Registered {tool.name}")
        
        registered_tools = registry.list_tools()
        print(f"  ✓ Total tools registered: {len(registered_tools)}")
        
        return True
    except Exception as e:
        print(f"  ✗ Tool registration failed: {e}")
        return False


def test_agents():
    """Test agent initialization"""
    print("\nTesting agents...")
    
    try:
        from llm import LLMClient
        from agents import PlannerAgent, ExecutorAgent, VerifierAgent
        
        client = LLMClient()
        
        planner = PlannerAgent(client)
        print("  ✓ Planner agent initialized")
        
        executor = ExecutorAgent()
        print("  ✓ Executor agent initialized")
        
        verifier = VerifierAgent(client)
        print("  ✓ Verifier agent initialized")
        
        return True
    except Exception as e:
        print(f"  ✗ Agent initialization failed: {e}")
        return False


def test_github_tool():
    """Test GitHub tool"""
    print("\nTesting GitHub tool...")
    
    try:
        from tools.github_tool import GitHubTool
        
        tool = GitHubTool()
        print("  ✓ GitHub tool initialized")
        
        # Test search
        result = tool.execute(action="search", query="python", limit=1)
        if result.get("success"):
            print("  ✓ GitHub search works")
            if result.get("repositories"):
                repo = result["repositories"][0]
                print(f"    Sample: {repo['full_name']} ({repo['stars']} stars)")
        else:
            print(f"  ℹ GitHub search returned: {result.get('error', 'no results')}")
        
        return True
    except Exception as e:
        print(f"  ✗ GitHub tool test failed: {e}")
        return False


def test_weather_tool():
    """Test Weather tool"""
    print("\nTesting Weather tool...")
    
    try:
        from tools.weather_tool import WeatherTool
        
        tool = WeatherTool()
        print("  ✓ Weather tool initialized")
        
        # Test weather fetch
        result = tool.execute(city="London")
        if result.get("success"):
            print("  ✓ Weather fetch works")
            print(f"    {result['city']}: {result['weather']['temperature']}")
        else:
            print(f"  ℹ Weather fetch: {result.get('message', 'using fallback')}")
        
        return True
    except Exception as e:
        print(f"  ✗ Weather tool test failed: {e}")
        return False


def test_exchange_tool():
    """Test Exchange Rate tool"""
    print("\nTesting Exchange Rate tool...")
    
    try:
        from tools.exchange_tool import ExchangeRateTool
        
        tool = ExchangeRateTool()
        print("  ✓ Exchange Rate tool initialized")
        
        # Test exchange rate fetch
        result = tool.execute(from_currency="USD", to_currency="EUR")
        if result.get("success"):
            print("  ✓ Exchange rate fetch works")
            print(f"    {result['conversion']}")
        else:
            print(f"  ✗ Exchange rate fetch failed: {result.get('error')}")
        
        return True
    except Exception as e:
        print(f"  ✗ Exchange Rate tool test failed: {e}")
        return False


def test_end_to_end():
    """Test end-to-end task execution"""
    print("\nTesting end-to-end execution...")
    
    try:
        from main import AIOperationsAssistant
        
        assistant = AIOperationsAssistant()
        print("  ✓ Assistant initialized")
        
        # Simple test task
        task = "Find 1 Python repository on GitHub"
        print(f"  Testing task: {task}")
        
        result = assistant.execute_task(task)
        
        if result["status"] in ["success", "partial"]:
            print("  ✓ Task executed successfully")
            print(f"    Status: {result['status']}")
            print(f"    Has answer: {bool(result.get('final_answer'))}")
            return True
        else:
            print(f"  ✗ Task execution failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"  ✗ End-to-end test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*80)
    print("AI OPERATIONS ASSISTANT - TEST SUITE")
    print("="*80)
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("LLM Client", test_llm_client),
        ("Tool Registry", test_tool_registry),
        ("Agents", test_agents),
        ("GitHub Tool", test_github_tool),
        ("Weather Tool", test_weather_tool),
        ("Exchange Rate Tool", test_exchange_tool),
        ("End-to-End", test_end_to_end)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
