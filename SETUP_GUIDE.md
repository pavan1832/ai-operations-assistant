# AI Operations Assistant - Setup & Usage Guide

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Anthropic API key (required)
- Git (for cloning repositories)

### 2. Installation

```bash
# Navigate to the project directory
cd ai_ops_assistant

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Configuration

Edit the `.env` file and add your API keys:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional (for enhanced features)
GITHUB_TOKEN=your_github_token_here
OPENWEATHER_API_KEY=your_openweather_key_here
NEWS_API_KEY=your_news_api_key_here
```

**Getting API Keys:**

- **Anthropic API Key** (Required): Get from https://console.anthropic.com/
- **GitHub Token** (Optional): Create at https://github.com/settings/tokens
  - Increases rate limits for GitHub API
  - No special permissions needed for public repositories
- **OpenWeather API Key** (Optional): Register at https://openweathermap.org/api
  - Free tier available
  - System uses fallback API if not provided
- **NewsAPI Key** (Optional): Get from https://newsapi.org/
  - Free tier available
  - System uses fallback if not provided

### 4. Verify Installation

Run the test suite to ensure everything is working:

```bash
python test.py
```

You should see output showing all tests passing:
```
✓ PASS: Imports
✓ PASS: Environment
✓ PASS: LLM Client
...
Total: 9/9 tests passed
🎉 All tests passed!
```

## Usage

### CLI Mode (Command Line)

Basic usage:
```bash
python main.py "Your task here"
```

Examples:
```bash
# GitHub operations
python main.py "Find the top 5 machine learning repositories"
python main.py "Search for Python web frameworks on GitHub"

# Weather queries
python main.py "What's the weather in Tokyo?"
python main.py "Get current weather for London"

# News queries
python main.py "Show me the latest technology news"
python main.py "Get top business headlines"

# Currency exchange
python main.py "What's the USD to EUR exchange rate?"
python main.py "Convert 100 GBP to JPY"

# Complex multi-tool tasks
python main.py "Find AI repositories on GitHub and get weather in San Francisco"
```

Verbose mode (shows detailed logs):
```bash
python main.py --verbose "Find Python repositories"
```

### API Mode (REST API)

Start the API server:
```bash
python main.py --api
```

The server will start on `http://localhost:8000` by default.

**Available Endpoints:**

1. **POST /execute** - Execute a task
   ```bash
   curl -X POST http://localhost:8000/execute \
     -H "Content-Type: application/json" \
     -d '{"task": "Find popular AI repositories on GitHub"}'
   ```

2. **GET /health** - Health check
   ```bash
   curl http://localhost:8000/health
   ```

3. **GET /tools** - List available tools
   ```bash
   curl http://localhost:8000/tools
   ```

Custom host and port:
```bash
python main.py --api --host 0.0.0.0 --port 8080
```

### Demo Mode

Run interactive demos:
```bash
python demo.py
```

This will show you various examples of what the system can do.

## Architecture Overview

### Multi-Agent System

The system uses three specialized agents:

1. **Planner Agent**
   - Analyzes the user's task
   - Breaks it down into executable steps
   - Selects appropriate tools for each step
   - Creates a structured execution plan

2. **Executor Agent**
   - Executes the plan step-by-step
   - Calls the necessary tools/APIs
   - Handles retries on failures
   - Manages step dependencies

3. **Verifier Agent**
   - Validates execution results
   - Checks for completeness
   - Generates natural language answers
   - Identifies if retries are needed

### Available Tools

| Tool | Description | API Key Required |
|------|-------------|------------------|
| **GitHub** | Search repositories, get repo details | Optional (GITHUB_TOKEN) |
| **Weather** | Current weather for any city | Optional (OPENWEATHER_API_KEY) |
| **News** | Latest news headlines by category | Optional (NEWS_API_KEY) |
| **Exchange Rate** | Currency conversion rates | No |

### Execution Flow

```
User Task
    ↓
Planner Agent (creates execution plan)
    ↓
Executor Agent (executes plan, calls tools)
    ↓
Verifier Agent (validates results)
    ↓
Final Answer
```

## Example Tasks

### Simple Tasks

**GitHub Search:**
```bash
python main.py "Find popular JavaScript frameworks"
```

**Weather Query:**
```bash
python main.py "What's the weather in Paris?"
```

**News Headlines:**
```bash
python main.py "Get latest sports news"
```

**Currency Exchange:**
```bash
python main.py "What's the current EUR to USD rate?"
```

### Complex Multi-Tool Tasks

**Research Task:**
```bash
python main.py "Find the top 3 data science repositories on GitHub and get the weather in Seattle"
```

**Information Gathering:**
```bash
python main.py "Get technology news and show me AI-related GitHub projects"
```

**Financial + Technical:**
```bash
python main.py "What's the USD to GBP rate and find finance-related Python repositories?"
```

## Response Format

CLI responses include:
- Task description
- Final answer (natural language)
- Status (success/partial/error)
- Verification status

API responses return JSON:
```json
{
  "task": "Find popular AI repositories",
  "status": "success",
  "plan": { ... },
  "execution": { ... },
  "verification": { ... },
  "final_answer": "Natural language response here..."
}
```

## Troubleshooting

### "No API key found"

**Problem:** ANTHROPIC_API_KEY not set

**Solution:**
1. Create a `.env` file in the project directory
2. Add: `ANTHROPIC_API_KEY=your_key_here`
3. Get a key from https://console.anthropic.com/

### GitHub Rate Limit Exceeded

**Problem:** Too many GitHub API requests

**Solution:**
1. Add `GITHUB_TOKEN` to `.env` file
2. Create token at https://github.com/settings/tokens
3. No special permissions needed for public repos

### Weather/News API Not Working

**Problem:** Weather or news data not available

**Solution:**
- These features are optional
- System will use fallback data if API keys not provided
- For real data, add the respective API keys to `.env`

### Import Errors

**Problem:** Module not found errors

**Solution:**
```bash
pip install -r requirements.txt
```

### Port Already in Use (API mode)

**Problem:** Port 8000 already in use

**Solution:**
```bash
python main.py --api --port 8080
```

## Advanced Usage

### Adding Custom Tools

1. Create a new tool class in `tools/`:
```python
from tools import BaseTool

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="What this tool does",
            parameters={
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                }
            }
        )
    
    def execute(self, **kwargs):
        # Implementation
        return {"result": "data"}
```

2. Register in `main.py`:
```python
from tools.my_tool import MyTool

def _register_tools(self):
    registry = get_registry()
    registry.register(MyTool())
```

### Customizing Agents

Agents can be customized by modifying their prompts and parameters:

- **Planner:** Edit `agents/planner.py` - adjust `temperature` or system prompt
- **Executor:** Edit `agents/executor.py` - change `max_retries` or `retry_delay`
- **Verifier:** Edit `agents/verifier.py` - modify validation logic

### Environment Variables

All available environment variables:

```bash
# Required
ANTHROPIC_API_KEY=your_key

# Optional API keys
GITHUB_TOKEN=your_token
OPENWEATHER_API_KEY=your_key
NEWS_API_KEY=your_key

# API server config
API_HOST=localhost
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

## Performance Notes

- **Average task completion:** 3-8 seconds
- **Cost per request:** ~$0.01-0.05 (varies by complexity)
- **Rate limits:** Depends on your Anthropic plan
- **API caching:** Not yet implemented (future improvement)

## Project Structure

```
ai_ops_assistant/
├── agents/                 # Agent implementations
│   ├── __init__.py
│   ├── planner.py         # Plans execution
│   ├── executor.py        # Executes steps
│   └── verifier.py        # Validates results
├── tools/                  # Tool implementations
│   ├── __init__.py
│   ├── github_tool.py
│   ├── weather_tool.py
│   ├── news_tool.py
│   └── exchange_tool.py
├── llm/                    # LLM client
│   ├── __init__.py
│   └── client.py
├── main.py                 # Entry point
├── demo.py                 # Demo script
├── test.py                 # Test suite
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── README.md              # Documentation
```

## Support & Feedback

For issues or questions:
1. Check this guide's troubleshooting section
2. Review the test output: `python test.py`
3. Run with verbose mode: `python main.py --verbose "task"`
4. Check logs in console output

## License

This project is for educational and demonstration purposes.
