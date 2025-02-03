"""
MCP Tools Package

This package contains all MCP (Model Context Protocol) components:
- Tools: Executable functions that can be called by LLMs
- Resources: Data sources that can be accessed by LLMs
- Prompts: Templates for generating LLM messages
- System Prompts: Context providers for LLM sampling
"""

import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Import all MCP components
from app.services.mcp_service import mcp_service
from . import (example_prompts, example_resources, example_system_prompts,
               example_tool)

__all__ = [
    "mcp_service",
    "example_tool",
    "example_resources",
    "example_prompts",
    "example_system_prompts",
]

