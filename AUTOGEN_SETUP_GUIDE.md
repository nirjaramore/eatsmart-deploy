# AutoGen Setup Guide for EatSmartly

## 📦 Installed Components

### Core Frameworks
- **autogen-agentchat** (v0.7.5) - Multi-agent conversation framework
- **autogen-core** (v0.7.5) - Event-driven programming for scalable multi-agent systems
- **autogen-ext** (v0.7.5) - Extensions for external services (OpenAI, MCP, Docker)

## 🚀 Quick Start

### 1. Basic Agent Example

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main():
    # Create an AI agent
    agent = AssistantAgent(
        "nutrition_expert",
        OpenAIChatCompletionClient(model="gpt-4o")
    )
    
    # Ask the agent a question
    result = await agent.run(task="Analyze nutrition for Coca-Cola")
    print(result)

asyncio.run(main())
```

### 2. Multi-Agent Setup for EatSmartly

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Create specialized agents
data_collector = AssistantAgent(
    "data_collector",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    system_message="You fetch nutrition data from multiple sources"
)

health_analyzer = AssistantAgent(
    "health_analyzer", 
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    system_message="You analyze nutrition and calculate health scores"
)

recommendation_agent = AssistantAgent(
    "recommendation_agent",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    system_message="You suggest healthier alternatives"
)

# Create team
team = RoundRobinGroupChat([data_collector, health_analyzer, recommendation_agent])

# Run analysis
result = await team.run(task="Analyze barcode 8901262010320")
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# OpenAI for AutoGen
OPENAI_API_KEY=your_openai_key_here

# Or use Azure OpenAI
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

## 📊 Use Cases for EatSmartly

### 1. Multi-Source Data Collection
- Agent 1: Fetches from OpenFoodFacts
- Agent 2: Fetches from USDA API
- Agent 3: Fetches from RapidAPI
- Agent 4: Aggregates and resolves conflicts

### 2. Health Analysis Pipeline
- Agent 1: Calculates basic nutrition score
- Agent 2: Checks against WHO guidelines
- Agent 3: Identifies harmful ingredients
- Agent 4: Generates health verdict

### 3. Recommendation System
- Agent 1: Searches for alternatives
- Agent 2: Ranks by health score
- Agent 3: Filters by user preferences
- Agent 4: Generates personalized suggestions

## 🛠️ Advanced Features

### Model Context Protocol (MCP) Integration

```python
from autogen_ext.agents.mcp import MCPWorkbench

# Connect to MCP servers for external data
mcp_agent = MCPWorkbench(
    mcp_servers=["nutrition-api", "food-database"]
)
```

### Docker Code Execution

```python
from autogen_ext.code_executors import DockerCommandLineCodeExecutor

# Run code safely in Docker container
executor = DockerCommandLineCodeExecutor(
    image="python:3.10-slim"
)
```

### Distributed Agents

```python
from autogen_ext.runtimes import GrpcWorkerAgentRuntime

# Run agents on different servers
runtime = GrpcWorkerAgentRuntime(host="localhost", port=50051)
```

## 🎯 Next Steps

1. **Install OpenAI API key** in `.env`
2. **Create multi-agent orchestrator** for barcode analysis
3. **Implement consensus mechanism** for multi-source data
4. **Add event-driven workflows** for real-time analysis
5. **Build distributed system** for scalability

## 📚 Resources

- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [AgentChat Guide](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html)
- [Core Framework](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/index.html)
- [Examples](https://github.com/microsoft/autogen/tree/main/python/packages/autogen-agentchat/examples)

## ⚠️ Current Issues

1. **Pydantic version conflict**: FastAPI uses Pydantic v1, AutoGen uses v2
   - **Solution**: Upgrade FastAPI to 0.115+ (supports Pydantic v2)
   
2. **Protobuf version conflict**: google-ai uses protobuf v4, AutoGen uses v5
   - **Solution**: Upgrade google-ai-generativelanguage package

### Fix Commands

```bash
pip install --upgrade fastapi pydantic
pip install --upgrade google-ai-generativelanguage
```

## ✅ Verification

The barcode scanning fix is complete:
- ✅ Barcode and search now use same `food_products` table
- ✅ Data consistency verified (Amul Butter: 724 calories in both)
- ✅ AutoGen framework installed and ready
- ✅ `get_product_by_id()` method added for product lookup

Test with:
```bash
python test_barcode_vs_search.py
```
