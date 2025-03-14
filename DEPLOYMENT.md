# Deployment Architecture

## Container Architecture

```mermaid
flowchart TB
 subgraph LB[Load Balancer]
  NX[NGINX]
 end

 subgraph APP[Application]
  API1[API 1]
  API2[API 2]
  API3[API n...]
 end

 subgraph DB[Storage]
  subgraph ES[Elasticsearch]
   ES1[(Node 1)]
   ES2[(Node 2)]
   ES3[(Node n)]
  end
  
  subgraph RD[Redis]
   RD1[(Master)]
   RD2[(Replica 1)]
   RD3[(Replica n)]
  end
 end

 subgraph MON[Monitoring]
  PM[Prometheus]
  GF[Grafana]
  AE[Alerts]
 end

 NX --> API1
 NX --> API2
 NX --> API3

 API1 --> ES1
 API1 --> RD1
 API2 --> ES1
 API2 --> RD1
 API3 --> ES1
 API3 --> RD1

 ES1 <--> ES2
 ES1 <--> ES3
 ES2 <--> ES3

 RD1 --> RD2
 RD1 --> RD3

 API1 --> PM
 API2 --> PM
 API3 --> PM
 PM --> GF
 PM --> AE
```

## Deployment Methods

### Using Docker Compose

The project includes a Docker Compose setup for quick deployment:

```bash
# Build and start all services
docker compose up -d

# Scale API servers if needed
docker compose up -d --scale web=3
```

### Production Deployment with Docker

Our Docker image uses Poetry for dependency management, ensuring consistent environments across all deployments:

1. Pull the image:
   ```bash
   docker pull myaiserv/api:latest
   ```

2. Run with proper environment variables:
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e DATABASE_URL=<db-url> \
     -e REDIS_URL=<redis-url> \
     -e ES_URL=<elasticsearch-url> \
     -v /path/to/logs:/app/logs \
     myaiserv/api:latest
   ```

## Deployment Configuration

### Container Orchestration

- Kubernetes or Docker Swarm for container orchestration
- Automatic scaling based on load
- Health checks and auto-recovery
- Rolling updates with zero downtime

### High Availability

- Multiple API server instances
- Elasticsearch cluster with 3+ nodes
- Redis master-replica setup
- Load balancer with SSL termination

### Monitoring & Alerts

- Real-time metrics collection
- Custom Grafana dashboards
- Alert rules for critical conditions
- Automated incident response

### Backup & Recovery

- Automated Elasticsearch snapshots
- Redis persistence and backup
- Configuration backups
- Disaster recovery procedures

### Security

- SSL/TLS encryption
- Network isolation
- Access control lists
- Security monitoring

## Resource Requirements

### Minimum Production Setup

- **API Servers**: 2+ instances, 2 CPU, 4GB RAM each
- **Elasticsearch**: 3 nodes, 4 CPU, 8GB RAM each
- **Redis**: 1 master + 2 replicas, 2 CPU, 4GB RAM each
- **Monitoring**: 2 CPU, 4GB RAM
- **Storage**: 100GB+ per Elasticsearch node

## CI/CD Pipeline

Our CI/CD pipeline uses Poetry to ensure consistent environment across development, testing, and production:

1. **Build Phase**:
   - Install dependencies with Poetry
   - Run linters and formatters
   - Execute tests

2. **Packaging Phase**:
   - Build Docker image with Poetry dependencies
   - Push to container registry

3. **Deployment Phase**:
   - Pull latest image
   - Deploy with zero downtime
   - Run health checks

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://user:pass@localhost:5432/myaiserv` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `ES_URL` | Elasticsearch URL | `http://localhost:9200` |
| `LOG_LEVEL` | Application log level | `INFO` |
| `DEBUG` | Enable debug mode | `false` |
| `PORT` | Application port | `8000` |
| `HOST` | Bind address | `0.0.0.0` |
