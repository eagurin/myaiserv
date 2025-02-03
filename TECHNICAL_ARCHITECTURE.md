# Technical Architecture

## Data Flow Architecture

```mermaid
flowchart TB
	subgraph Clients
		WC[WebSocket]
		RC[REST]
		GC[GraphQL]
	end

	subgraph API
		FA[FastAPI]
		WH[WS Handler]
		RH[REST Handler]
		GH[GQL Handler]
		MM[Message Manager]
		
		FA --> WH
		FA --> RH
		FA --> GH
		WH --> MM
		RH --> MM
		GH --> MM
	end

	subgraph Core
		MCP[MCP Service]
		TM[Tool Manager]
		RM[Resource Manager]
		PM[Prompt Manager]
		TR[Tool Registry]
		RC2[Resource Cache]
		PL[Prompt Loader]
		
		MM --> MCP
		MCP --> TM
		MCP --> RM
		MCP --> PM
		TM --> TR
		RM --> RC2
		PM --> PL
	end

	subgraph Storage
		ES[(Elastic)]
		RD[(Redis)]
		
		subgraph ESI[ES Indices]
			VI[Vector]
			FI[Full-text]
			MI[Metadata]
		end
		
		subgraph RDS[Redis Store]
			CS[Cache]
			SS[Session]
			PS[PubSub]
		end
	end

	subgraph Monitor
		PE[Prometheus]
		PA[Alerts]
		GD[Grafana]
		
		PE --> PA
		PA --> GD
	end

	WC --> FA
	RC --> FA
	GC --> FA
	
	MCP --> ES
	MCP --> RD
	
	FA --> PE
```

## Component Details

### API Gateway
- **FastAPI Server**: Main entry point handling all incoming requests
- **WebSocket Handler**: Manages real-time bidirectional communication
- **REST Handler**: Processes HTTP requests for REST API
- **GraphQL Handler**: Handles GraphQL queries and mutations

### MCP Core
- **MCP Service**: Core service implementing Model Context Protocol
- **Tool Manager**: Handles tool registration and execution
- **Resource Manager**: Manages resource loading and caching
- **Prompt Manager**: Processes and manages system/user prompts

### Storage Layer
- **Elasticsearch**:
  - Vector Index: For semantic search
  - Full-text Index: For text search
  - Metadata Index: For storing relationships
- **Redis**:
  - Cache Store: For fast data access
  - Session Store: For user sessions
  - Pub/Sub: For real-time updates

### Monitoring
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards

## Data Flow Sequence

1. Client sends request through WebSocket/REST/GraphQL
2. FastAPI routes request to appropriate handler
3. Message Manager processes and validates request
4. MCP Service executes requested operation
5. Results are stored in Elasticsearch/Redis
6. Response is sent back to client
7. Metrics are collected by Prometheus