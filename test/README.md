# Test Environment

This directory contains a complete test environment setup for myaiserv with modified ports and configurations to avoid conflicts with the development environment.

## Services

- Web App: http://localhost:8001
- PostgreSQL: localhost:5433
- Elasticsearch: http://localhost:9201
- Kafka: localhost:9093
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9091

## Getting Started

1. Start the test environment:
```bash
docker-compose up -d
```

2. Monitor service health:
```bash
docker-compose ps
```

3. View logs:
```bash
docker-compose logs -f
```

## Environment Variables

All test-specific environment variables are defined in `.env` file with modified ports and credentials to avoid conflicts with development environment.

## Configuration

- Prometheus configuration: `config/prometheus/prometheus.yml`
- Grafana datasources: `config/grafana/provisioning/datasources/datasource.yml`

## Cleanup

To stop and remove all test containers and volumes:
```bash
docker-compose down -v
```