# MyAIServ: AI-Powered FastAPI Server with MCP 🚀

[![smithery badge](https://smithery.ai/badge/@eagurin/myaiserv)](https://smithery.ai/server/@eagurin/myaiserv)

High-performance FastAPI server implementing Model Context Protocol (MCP) for seamless integration with Large Language Models (LLMs). Built with modern stack: FastAPI, Elasticsearch, Redis, Prometheus, and Grafana.

[View Detailed Architecture](ARCHITECTURE.md)

## Core Features ✨

- FastAPI-powered REST, GraphQL, and WebSocket APIs
- Full MCP support (Tools, Resources, Prompts, Sampling)
- Vector search with Elasticsearch
- Real-time monitoring (Prometheus + Grafana)
- Docker-ready deployment
- Comprehensive test coverage

## Quick Start 🚀

### Installing via Smithery

To install AI-Powered FastAPI Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@eagurin/myaiserv):

```bash
npx -y @smithery/cli install @eagurin/myaiserv --client claude
```

### Manual Installation
```bash
# Clone and setup
git clone https://github.com/eagurin/myaiserv.git
cd myaiserv
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt

# Configure and run
cp .env.example .env
uvicorn app.main:app --reload
```

Access:

- API Docs: <http://localhost:8000/docs>
- GraphQL: <http://localhost:8000/graphql>

## Stack 🛠

- **Backend:** FastAPI, Python 3.8+
- **Storage:** Elasticsearch, Redis
- **Monitoring:** Prometheus, Grafana
- **Testing:** Pytest
- **Deployment:** Docker, Docker Compose

## License 📄

[MIT](LICENSE)
