# 🚀 Full-Scale Enhanced SciRAG Docker Deployment

This directory contains the complete production-ready Docker deployment for Enhanced SciRAG with RAGBook integration.

## 📁 Directory Structure

```
deployment/docker/
├── Dockerfile.production          # Full production Dockerfile
├── docker-compose.production.yml  # Complete production stack
├── requirements.production.txt    # Production dependencies
├── prometheus.yml                 # Prometheus monitoring config
├── grafana/                       # Grafana monitoring setup
│   ├── datasources/
│   └── dashboards/
├── scripts/
│   └── deploy-production.sh       # Production deployment script
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Deploy Full Production Stack

```bash
# From the scirag root directory
./deployment/docker/scripts/deploy-production.sh
```

### 2. Access Services

- **SciRAG API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## 🏗️ Architecture

### Services

1. **scirag-api**: Enhanced SciRAG API server
   - Port: 8000
   - Features: Mathematical processing, asset processing, glossary extraction
   - Health checks and metrics

2. **prometheus**: Metrics collection and monitoring
   - Port: 9090
   - Collects metrics from SciRAG API
   - Stores time-series data

3. **grafana**: Monitoring dashboards
   - Port: 3000
   - Visualizes Prometheus metrics
   - Pre-configured dashboards

### Volumes

- `markdown_files/`: Input documents
- `data/`: Processed data and embeddings
- `logs/`: Application logs
- `cache/`: Processing cache

## 🔧 Management Commands

```bash
# View all services
docker compose -f deployment/docker/docker-compose.production.yml ps

# View logs
docker compose -f deployment/docker/docker-compose.production.yml logs -f

# View specific service logs
docker compose -f deployment/docker/docker-compose.production.yml logs -f scirag-api

# Stop all services
docker compose -f deployment/docker/docker-compose.production.yml down

# Restart services
docker compose -f deployment/docker/docker-compose.production.yml restart

# Rebuild and restart
docker compose -f deployment/docker/docker-compose.production.yml up --build -d
```

## 🧪 Testing the API

### Test Mathematical Processing

```bash
curl -X POST http://localhost:8000/api/v2/process-document \
  -H 'Content-Type: application/json' \
  -d '{
    "content": "E = mc^2",
    "content_type": "equation"
  }'
```

### Test Document Processing

```bash
curl -X POST http://localhost:8000/api/v2/process-document \
  -H 'Content-Type: application/json' \
  -d '{
    "content": "The equation E = mc^2 represents mass-energy equivalence.",
    "content_type": "prose"
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

## 📊 Monitoring

### Prometheus Metrics

- Visit http://localhost:9090
- Query metrics: `scirag_requests_total`, `scirag_processing_duration_seconds`
- Set up alerts for production use

### Grafana Dashboards

- Visit http://localhost:3000
- Login with admin/admin
- Pre-configured dashboards for SciRAG metrics
- Custom dashboards for enhanced processing

## 🔒 Security Features

- Non-root user in containers
- Health checks for all services
- Resource limits and restart policies
- Secure volume mounts

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000, 3000, 9090 are available
2. **Memory issues**: Increase Docker memory allocation
3. **Build failures**: Check Docker logs for specific errors

### Debug Commands

```bash
# Check container status
docker ps -a

# Check container logs
docker logs <container_name>

# Check resource usage
docker stats

# Access container shell
docker exec -it <container_name> /bin/bash
```

## 📈 Production Considerations

1. **Resource Limits**: Set appropriate CPU/memory limits
2. **Persistent Storage**: Use named volumes for data persistence
3. **Backup Strategy**: Regular backups of data and configurations
4. **Monitoring**: Set up alerts and log aggregation
5. **Security**: Use secrets management for sensitive data

## 🔄 Updates and Maintenance

```bash
# Update dependencies
docker compose -f deployment/docker/docker-compose.production.yml build --no-cache

# Rolling update
docker compose -f deployment/docker/docker-compose.production.yml up -d --no-deps scirag-api

# Clean up old images
docker system prune -a
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Ready for production use! 🚀**
