"""
MCP Tools Package

This package contains all MCP (Model Context Protocol) components:
- Tools: Executable functions that can be called by LLMs
- Resources: Data sources that can be accessed by LLMs
- Prompts: Templates for generating LLM messages
- System Prompts: Context providers for LLM sampling

Usage:
        from app.tools import mcp_service

        # Access registered tools
        tools = await mcp_service.list_tools()

        # Access registered resources
        resources = await mcp_service.list_resources()

        # Access registered prompts
        prompts = await mcp_service.list_prompts()
"""

import asyncio
import logging
from typing import Any, Dict, List

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Import all MCP components
from app.services.mcp_service import mcp_service

from . import (example_prompts, example_resources, example_system_prompts,
               example_tool)


async def initialize_mcp():
    """Initialize all MCP components"""
    try:
        # Initialize tools
        tools = await mcp_service.list_tools()
        logger.info(f"Initialized {len(tools)} tools:")
        for tool in tools:
            logger.info(f"- {tool.name}: {tool.description}")

        # Initialize resources
        resources = await mcp_service.list_resources()
        logger.info(f"Initialized {len(resources)} resources:")
        for resource in resources:
            logger.info(f"- {resource.name}: {resource.uri}")

        # Initialize prompts
        prompts = await mcp_service.list_prompts()
        logger.info(f"Initialized {len(prompts)} prompts:")
        for prompt in prompts:
            logger.info(f"- {prompt.name}")

        logger.info("MCP initialization completed successfully")

    except Exception as e:
        logger.error(f"Error initializing MCP components: {str(e)}")
        raise


# Initialize components on import
try:
    loop = asyncio.get_event_loop()
    loop.create_task(initialize_mcp())
except Exception as e:
    logger.error(f"Failed to start initialization task: {str(e)}")

__all__ = [
    "mcp_service",
    "example_tool",
    "example_resources",
    "example_prompts",
    "example_system_prompts",
]
