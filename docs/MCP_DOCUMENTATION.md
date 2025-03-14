# Model Context Protocol Documentation

## Introduction

MCP is an open protocol that standardizes how applications provide context to LLMs. Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect your devices to various peripherals and accessories, MCP provides a standardized way to connect AI models to different data sources and tools.

## Core Architecture

### Overview

MCP follows a client-server architecture where:

- **Hosts** are LLM applications (like Claude Desktop or IDEs) that initiate connections
- **Clients** maintain 1:1 connections with servers, inside the host application
- **Servers** provide context, tools, and prompts to clients

### Key Components

1. **Resources**
   - File-like data that can be read by clients
   - Identified by unique URIs
   - Can contain text or binary data
   - Application-controlled access

2. **Tools**
   - Functions that can be called by the LLM
   - Model-controlled with user approval
   - Support various operations and integrations
   - Include input validation and error handling

3. **Prompts**
   - Pre-written templates for specific tasks
   - Support dynamic arguments
   - Include context from resources
   - Enable workflow automation

4. **Sampling**
   - Allows servers to request LLM completions
   - Maintains security and privacy
   - Supports model preferences
   - Includes context management

## Transport Layer

MCP supports multiple transport mechanisms:

1. **Stdio Transport**
   - Uses standard input/output for communication
   - Ideal for local processes
   - Simple process management

2. **HTTP with SSE Transport**
   - Server-Sent Events for server-to-client messages
   - HTTP POST for client-to-server messages
   - Suitable for network communication

## Security Considerations

- Authentication and authorization controls
- Input validation and sanitization
- Resource access restrictions
- Rate limiting and monitoring
- Secure transport protocols
- Error handling and logging

## Best Practices

1. **Implementation**
   - Follow SOLID principles
   - Use strong typing
   - Implement proper error handling
   - Add comprehensive logging

2. **Resource Management**
   - Validate all resource URIs
   - Implement proper cleanup
   - Handle concurrent access
   - Monitor resource usage

3. **Tool Development**
   - Clear documentation
   - Input validation
   - Error handling
   - Progress reporting

4. **Security**
   - Validate all inputs
   - Implement access controls
   - Monitor usage
   - Regular updates

## Getting Started

1. **Choose Your Role**
   - Server Developer: Build custom integrations
   - Client Developer: Create MCP-enabled applications
   - User: Utilize existing MCP servers

2. **Setup Environment**
   - Install required SDKs
   - Configure development environment
   - Set up testing tools

3. **Implementation Steps**
   - Design your integration
   - Implement core features
   - Test thoroughly
   - Deploy and monitor

## SDKs and Tools

- Python SDK
- TypeScript SDK
- MCP Inspector
- Development Tools
- Testing Utilities

## Community and Support

- GitHub Discussions
- Documentation
- Example Implementations
- Best Practices Guides

## Debugging

### Tools Overview

1. **MCP Inspector**
   - Interactive debugging interface
   - Direct server testing
   - Message flow visualization

2. **Claude Desktop Developer Tools**
   - Integration testing
   - Log collection
   - Chrome DevTools integration

3. **Server Logging**
   - Custom logging implementations
   - Error tracking
   - Performance monitoring

### Common Issues

1. **Working Directory**
   - Use absolute paths in configuration
   - Consider process start location
   - Handle path resolution correctly

2. **Environment Variables**
   - Inherit subset of variables
   - Configure through server config
   - Handle sensitive data properly

3. **Server Initialization**
   - Path resolution
   - Configuration validation
   - Environment setup
   - Permission checks

### Best Debugging Practices

1. **Logging Strategy**
   - Structured logging
   - Context inclusion
   - Error tracking
   - Performance metrics

2. **Testing Workflow**
   - Use Inspector for basic testing
   - Implement integration tests
   - Monitor logs
   - Check error handling

## Example Servers

### Official Reference Implementations

1. **Data and File Systems**
   - Filesystem server
   - PostgreSQL server
   - SQLite server
   - Google Drive integration

2. **Development Tools**
   - Git server
   - GitHub integration
   - GitLab integration
   - Sentry integration

3. **Web and Browser**
   - Brave Search
   - Fetch utilities
   - Puppeteer automation

4. **Productivity**
   - Slack integration
   - Google Maps
   - Memory management

### Community Servers

- Docker management
- Kubernetes control
- Linear integration
- Snowflake database
- Spotify control
- Todoist management

## Future Development

### Roadmap

1. **Remote MCP Support**
   - Authentication & Authorization
   - Service Discovery
   - Stateless Operations

2. **Reference Implementations**
   - Client Examples
   - Protocol Drafting

3. **Distribution & Discovery**
   - Package Management
   - Installation Tools
   - Server Registry

4. **Agent Support**
   - Hierarchical Agent Systems
   - Interactive Workflows
   - Streaming Results

### Standardization

- Community-Led Development
- Additional Modalities
- Standardization Process

## Protocol Details

### Message Format

MCP uses JSON-RPC 2.0 for message exchange:

1. **Requests**
```json
{
    "jsonrpc": "2.0",
    "id": "unique-id",
    "method": "method-name",
    "params": {}
}
```

2. **Responses**
```json
{
    "jsonrpc": "2.0",
    "id": "unique-id",
    "result": {}
}
```

3. **Notifications**
```json
{
    "jsonrpc": "2.0",
    "method": "notification-name",
    "params": {}
}
```

### Connection Lifecycle

1. **Initialization**
     - Client sends initialize request
     - Server responds with capabilities
     - Client sends initialized notification

2. **Operation**
     - Request/response exchanges
     - Notifications as needed
     - Tool execution
     - Resource access

3. **Termination**
     - Clean shutdown
     - Resource cleanup
     - Connection closure

## Implementation Examples

### Basic Server Example

```python
from mcp.server import Server
import mcp.types as types

app = Server("example-server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
        return [
                types.Tool(
                        name="example-tool",
                        description="An example tool",
                        inputSchema={
                                "type": "object",
                                "properties": {
                                        "param": {"type": "string"}
                                }
                        }
                )
        ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> str:
        if name == "example-tool":
                return f"Tool executed with: {arguments['param']}"
        raise ValueError(f"Unknown tool: {name}")
```

### Basic Client Example

```typescript
import { Client } from "@modelcontextprotocol/sdk/client";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio";

const client = new Client({
    name: "example-client",
    version: "1.0.0"
});

const transport = new StdioClientTransport({
    command: "./server",
    args: []
});

await client.connect(transport);
const tools = await client.listTools();
```

## Error Handling

### Standard Error Codes

```typescript
enum ErrorCode {
    ParseError = -32700,
    InvalidRequest = -32600,
    MethodNotFound = -32601,
    InvalidParams = -32602,
    InternalError = -32603
}
```

### Error Response Format

```json
{
    "jsonrpc": "2.0",
    "id": "request-id",
    "error": {
        "code": -32700,
        "message": "Parse error",
        "data": {}
    }
}
```

### Error Handling Best Practices

1. **Client-Side**
     - Validate requests before sending
     - Handle timeouts appropriately
     - Implement retry logic
     - Log errors for debugging

2. **Server-Side**
     - Validate all inputs
     - Return appropriate error codes
     - Include helpful error messages
     - Maintain audit logs
