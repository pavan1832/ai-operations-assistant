#!/usr/bin/env python3
"""
Demo script for AI Operations Assistant
Demonstrates various capabilities and use cases
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import AIOperationsAssistant


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(title.center(80))
    print("="*80 + "\n")


def print_result(result):
    """Print a formatted result"""
    print("-"*80)
    print("RESULT")
    print("-"*80)
    print(result["final_answer"])
    print()
    print(f"Status: {result['status']}")
    if result.get("verification"):
        print(f"Verified: {result['verification'].get('verified', False)}")
    print("-"*80 + "\n")


def demo_github_search():
    """Demo GitHub repository search"""
    print_header("DEMO 1: GitHub Repository Search")
    
    assistant = AIOperationsAssistant()
    
    tasks = [
        "Find the top 3 machine learning repositories on GitHub",
        "Search for Python web frameworks on GitHub",
        "Show me popular AI repositories"
    ]
    
    for task in tasks:
        print(f"Task: {task}\n")
        result = assistant.execute_task(task)
        print_result(result)
        time.sleep(2)


def demo_weather():
    """Demo weather queries"""
    print_header("DEMO 2: Weather Information")
    
    assistant = AIOperationsAssistant()
    
    tasks = [
        "What's the weather like in London?",
        "Get the current weather in Tokyo",
        "Tell me about the weather in New York"
    ]
    
    for task in tasks:
        print(f"Task: {task}\n")
        result = assistant.execute_task(task)
        print_result(result)
        time.sleep(2)


def demo_news():
    """Demo news queries"""
    print_header("DEMO 3: News Headlines")
    
    assistant = AIOperationsAssistant()
    
    tasks = [
        "Get the latest technology news",
        "Show me recent business headlines",
        "What are the top news stories today?"
    ]
    
    for task in tasks:
        print(f"Task: {task}\n")
        result = assistant.execute_task(task)
        print_result(result)
        time.sleep(2)


def demo_exchange_rates():
    """Demo currency exchange rates"""
    print_header("DEMO 4: Currency Exchange Rates")
    
    assistant = AIOperationsAssistant()
    
    tasks = [
        "What's the USD to EUR exchange rate?",
        "Convert 100 GBP to JPY",
        "Show me the current EUR to USD rate"
    ]
    
    for task in tasks:
        print(f"Task: {task}\n")
        result = assistant.execute_task(task)
        print_result(result)
        time.sleep(2)


def demo_multi_tool():
    """Demo multi-tool orchestration"""
    print_header("DEMO 5: Multi-Tool Orchestration")
    
    assistant = AIOperationsAssistant()
    
    tasks = [
        "Find Python web frameworks on GitHub and get the weather in San Francisco",
        "Get the latest tech news and show me AI repositories on GitHub",
        "What's the USD to EUR rate and find finance-related repositories"
    ]
    
    for task in tasks:
        print(f"Task: {task}\n")
        result = assistant.execute_task(task)
        print_result(result)
        time.sleep(2)


def main():
    """Run all demos"""
    load_dotenv()
    
    print_header("AI OPERATIONS ASSISTANT - DEMO")
    print("This demo showcases the multi-agent AI system's capabilities")
    print("Each demo will execute several tasks using different tools\n")
    
    input("Press Enter to start...")
    
    demos = [
        ("GitHub Search", demo_github_search),
        ("Weather Info", demo_weather),
        ("News Headlines", demo_news),
        ("Exchange Rates", demo_exchange_rates),
        ("Multi-Tool Tasks", demo_multi_tool)
    ]
    
    print("\nAvailable demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"{i}. {name}")
    print(f"{len(demos) + 1}. Run all demos")
    
    choice = input("\nSelect demo number (or press Enter to run all): ").strip()
    
    if not choice:
        choice = str(len(demos) + 1)
    
    try:
        choice_num = int(choice)
        
        if choice_num == len(demos) + 1:
            # Run all demos
            for name, demo_func in demos:
                try:
                    demo_func()
                except Exception as e:
                    print(f"\nError in {name}: {str(e)}\n")
                    continue
        elif 1 <= choice_num <= len(demos):
            # Run selected demo
            name, demo_func = demos[choice_num - 1]
            demo_func()
        else:
            print("Invalid choice")
            return
            
    except ValueError:
        print("Invalid input")
        return
    
    print_header("DEMO COMPLETE")
    print("Thank you for trying the AI Operations Assistant!")


if __name__ == "__main__":
    main()
