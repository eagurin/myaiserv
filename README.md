# FastAPI MCP Server: Your Powerful AI-Powered Application 🚀

This project showcases a cutting-edge FastAPI server leveraging the Model Context Protocol (MCP) for seamless integration with Large Language Models (LLMs).  It's designed for speed, scalability, and ease of use, making it the perfect foundation for your next AI-driven application.

## Key Features ✨

- **Blazing-Fast Performance:** Built with FastAPI for optimal speed and efficiency.
- **Flexible Data Storage:** Uses Elasticsearch for powerful full-text and vector search, and Redis for lightning-fast caching.
- **Robust MCP Implementation:**  Supports all core MCP features: Tools, Resources, Prompts, and Sampling.
- **GraphQL Integration:**  Provides a flexible GraphQL API for easy data access.
- **Comprehensive Monitoring:**  Includes Prometheus metrics and Grafana dashboards for real-time monitoring and alerting.
- **Modular Design:**  Clean, well-structured code for easy maintenance and extension.
- **Thorough Testing:**  Includes unit and integration tests for robust reliability.
- **Easy Deployment:**  Dockerized for simple and consistent deployment.

## Getting Started 🛠️

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd myaiserv
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**  Copy `.env.example` to `.env` and adjust the values to match your environment.
5. **Run the application:**

   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API:**
   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - GraphQL Playground: [http://localhost:8000/graphql](http://localhost:8000/graphql)

## Usage Examples 💡

### REST API

```python
import httpx
import asyncio

async def main():
 async with httpx.AsyncClient() as client:
  # Get a list of tools
  response = await client.get("http://localhost:8000/tools")
  print(response.json())

  # Execute a tool
  result = await client.post(
   "http://localhost:8000/tools/weather",
   json={"latitude": 37.7749, "longitude": -122.4194}
  )
  print(result.json())

asyncio.run(main())
```

### GraphQL

```graphql
query {
  listTools {
 name
 description
  }
}

mutation {
  executeTool(
 name: "weather"
 parameters: {
   latitude: 37.7749
   longitude: -122.4194
 }
  ) {
 content {
   text
 }
  }
}
```

### WebSocket

```python
import asyncio
import websockets
import json

async def main():
 async with websockets.connect("ws://localhost:8000/mcp") as websocket:
  await websocket.send(json.dumps({"jsonrpc": "2.0", "method": "initialize"}))
  response = await websocket.recv()
  print(response)

asyncio.run(main())
```

## Project Structure 📁

```
myaiserv/
├── app/
│   ├── core/             # Core MCP components
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic
│   ├── storage/         # Database interactions
│   ├── tools/           # MCP tools
│   └── main.py         # FastAPI application
├── config/             # Configuration files
├── docs/               # Documentation
├── migrations/         # Database migrations
├── scripts/            # Utility scripts
├── tests/              # Tests
└── requirements.txt   # Project dependencies
```

## Contributing 🤝

We welcome contributions! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for how to get started.

## License 📄

[MIT](LICENSE)
