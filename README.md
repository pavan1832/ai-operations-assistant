# AI Operations Assistant

A multi-agent AI system that accepts natural language tasks, plans execution steps, calls real APIs, and returns structured answers.

## Architecture

This system implements a three-agent architecture:

- **Planner Agent**: Converts user input into structured step-by-step plans
- **Executor Agent**: Executes planned steps and calls external APIs
- **Verifier Agent**: Validates results and ensures output quality

## Features

- ✅ Multi-agent reasoning with LLM-powered decision making
- ✅ Real API integrations (GitHub, Weather, News, Exchange Rates)
- ✅ Structured JSON outputs with schema validation
- ✅ Error handling with automatic retries
- ✅ Both CLI and REST API interfaces
- ✅ Comprehensive logging and debugging

## Installation

1. **Clone and navigate to the project:**
```bash
cd ai_ops_assistant
```
2. **Create Virtual Environment:**
```bash
python -m venv venv

#Activate it
# on windows:
venv\Scripts\activate
#on Max/Linux:
source venv/bin/activate

#Caution: Consider only if you encounter any errors if else ignore this
if you encounter Unauthorized access while running this run the following code
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

```

3. **Install dependencies:**
```bash
pip install -r requirements.txt

#Caution: Consider only if you encounter any errors if else ignore this
if your pip dependency is 2.5.3 or lower and encountering incompatible upgrade it
pip install --upgrade "pydantic>=2.9,<3"
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Usage

### CLI Mode

```bash
# Basic usage
python main.py "Find the top 3 Python repositories on GitHub"

# Complex multi-tool tasks
python main.py "Get the weather in London and find GitHub repos about weather APIs"

# With verbose logging
python main.py --verbose "What's the current USD to EUR exchange rate?"
```

### API Mode

```bash
# Start the server
python main.py --api

Required API keys:
- `Gemini_API_KEY`: Your Gemini API key (required)
- `GITHUB_TOKEN`: GitHub personal access token (optional, increases rate limits)
- `OPENWEATHER_API_KEY`: OpenWeatherMap API key (optional, for weather data)
- `NEWS_API_KEY`: NewsAPI key (optional, for news data)

### API Mode

```bash
# Start the server
python main.py --api

# In another terminal, make requests:
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Find popular AI repositories on GitHub"}'
```

## Example Tasks

```bash
# GitHub integration
python main.py "Show me the top 5 machine learning repositories"

# Weather integration
python main.py "What's the weather like in Tokyo?"

# News integration
python main.py "Get the latest technology news headlines"

# Exchange rates
python main.py "What's the USD to GBP exchange rate?"

# Multi-tool orchestration
python main.py "Find Python web frameworks on GitHub and get weather in San Francisco"
```

## API Endpoints

### POST /execute
Execute a natural language task.

**Request:**
```json
{
  "task": "Find the top 3 AI repositories on GitHub"
}
```

**Response:**
```json
{
  "task": "Find the top 3 AI repositories on GitHub",
  "status": "success",
  "plan": {
    "steps": [...],
    "tools": [...]
  },
  "results": [...],
  "final_answer": "..."
}
```

### GET /health
Check API health status.

## Project Structure

```
ai_ops_assistant/
├── agents/
│   ├── __init__.py
│   ├── planner.py      # Plans task execution
│   ├── executor.py     # Executes steps and calls APIs
│   └── verifier.py     # Validates and formats results
├── tools/
│   ├── __init__.py
│   ├── github_tool.py  # GitHub API integration
│   ├── weather_tool.py # Weather API integration
│   ├── news_tool.py    # News API integration
│   └── exchange_tool.py # Currency exchange rates
├── llm/
│   ├── __init__.py
│   └── client.py       # LLM client wrapper
├── main.py             # Entry point (CLI & API)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## Development

### Adding New Tools

1. Create a new tool class in `tools/`:
```python
from tools import BaseTool

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="What this tool does"
        )
    
    def execute(self, **kwargs):
        # Implementation
        return {"result": "data"}
```

2. Register in `tools/__init__.py`
3. Tool will be automatically available to agents

### Running Tests

```bash
# Test individual components
python -c "from agents.planner import PlannerAgent; print('Planner OK')"
python -c "from tools.github_tool import GitHubTool; print('GitHub Tool OK')"

# End-to-end test
python main.py "Test task: Find a Python repository"
```

## Architecture Details

### Agent Flow

1. **User Input** → Natural language task
2. **Planner Agent** → Analyzes task, creates execution plan
3. **Executor Agent** → Runs each step, calls appropriate tools
4. **Verifier Agent** → Validates results, ensures completeness
5. **Output** → Structured JSON response

### LLM Integration

- Uses Claude Sonnet 4.5 for agent reasoning
- Structured outputs with JSON schema constraints
- Separate prompts for each agent role
- Temperature tuning per agent (Planner: 0.3, Verifier: 0.2)

### Error Handling

- Automatic retry on API failures (max 3 attempts)
- Graceful degradation with partial results
- Detailed error messages in responses
- Fallback strategies for missing data

## Performance Notes

- Average task completion: 3-8 seconds
- Concurrent tool execution: Not yet implemented
- API response caching: Not yet implemented
- Cost per request: ~$0.01-0.05 (depending on complexity)

## Future Improvements

- [ ] Parallel tool execution for independent steps
- [ ] API response caching to reduce costs
- [ ] Cost tracking dashboard
- [ ] Streaming responses for long-running tasks
- [ ] User session management
- [ ] Tool usage analytics

## Troubleshooting

**Issue**: "No API key found"
- Solution: Ensure `.env` file exists with `ANTHROPIC_API_KEY`

**Issue**: GitHub rate limit exceeded
- Solution: Add `GITHUB_TOKEN` to `.env` file

**Issue**: Weather/News API not working
- Solution: These are optional. System will skip if API keys not provided.

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please check the troubleshooting section above.
