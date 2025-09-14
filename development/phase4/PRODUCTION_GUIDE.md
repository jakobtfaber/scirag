# Enhanced SciRAG Production Guide

## 🚀 Overview

This guide provides comprehensive instructions for deploying and managing the Enhanced SciRAG system in production. The system includes RAGBook integration for advanced mathematical content processing, comprehensive monitoring, and enterprise-grade features.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended) or macOS
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ recommended
- **Storage**: 20GB+ available space
- **Network**: Internet access for API calls

### Software Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.12+ (for local development)
- **Git**: 2.0+

## 🏗️ Architecture

### Components
- **API Server**: FastAPI-based REST API
- **Enhanced Processing**: Mathematical, asset, and glossary processing
- **Monitoring**: Prometheus + Grafana
- **Caching**: Redis
- **Database**: SQLite (configurable)
- **Load Balancer**: Nginx (optional)

### Services
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   SciRAG API    │    │   Redis         │
│   (Load Balancer)│    │   (FastAPI)     │    │   (Caching)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Monitoring    │
                    │   (Prometheus   │
                    │   + Grafana)    │
                    └─────────────────┘
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd scirag
chmod +x scripts/*.sh
```

### 2. Deploy with Docker Compose
```bash
# Deploy all services
./scripts/deploy.sh

# Or manually
docker-compose up -d
```

### 3. Verify Deployment
```bash
# Run production tests
python scripts/test_production.py

# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs -f
```

## ⚙️ Configuration

### Environment Variables

#### Core Settings
```bash
SCIRAG_CORPUS_NAME=enhanced_scirag_corpus
SCIRAG_MARKDOWN_FILES_PATH=/app/markdown_files
SCIRAG_GEN_MODEL=gemini-1.5-pro
```

#### Enhanced Processing
```bash
SCIRAG_ENHANCED_PROCESSING=true
SCIRAG_MATH_PROCESSING=true
SCIRAG_ASSET_PROCESSING=true
SCIRAG_GLOSSARY_EXTRACTION=true
```

#### Performance
```bash
SCIRAG_CHUNK_SIZE=320
SCIRAG_OVERLAP_RATIO=0.12
SCIRAG_MAX_CONCURRENT_REQUESTS=10
SCIRAG_REQUEST_TIMEOUT=30
```

#### API Settings
```bash
SCIRAG_API_HOST=0.0.0.0
SCIRAG_API_PORT=8000
SCIRAG_API_WORKERS=4
```

#### Monitoring
```bash
SCIRAG_LOG_LEVEL=INFO
SCIRAG_ENABLE_METRICS=true
SCIRAG_ENABLE_ALERTING=true
```

### Configuration File
Create `config/production.json`:
```json
{
  "core": {
    "corpus_name": "enhanced_scirag_corpus",
    "markdown_files_path": "./markdown_files",
    "gen_model": "gemini-1.5-pro"
  },
  "enhanced_processing": {
    "enabled": true,
    "mathematical_processing": true,
    "asset_processing": true,
    "glossary_extraction": true
  },
  "performance": {
    "max_memory_usage": 2048,
    "max_cpu_usage": 80,
    "max_response_time": 5.0,
    "max_error_rate": 0.05
  }
}
```

## 🔧 API Usage

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Health Check
```bash
GET /health
```
Returns system health status and component information.

#### Query Documents
```bash
POST /query
Content-Type: application/json

{
  "query": "What is the theory of relativity?",
  "content_types": ["prose", "equation"],
  "max_results": 10,
  "enable_enhanced_processing": true
}
```

#### Upload Document
```bash
POST /documents
Content-Type: application/json

{
  "content": "# Document Title\n\nContent here...",
  "source_id": "doc_001",
  "file_type": "markdown"
}
```

#### Get Metrics
```bash
GET /metrics
```
Returns system performance metrics.

#### Get Configuration
```bash
GET /config
```
Returns current system configuration.

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Monitoring

### Prometheus
- **URL**: http://localhost:9090
- **Metrics**: System performance, API metrics, custom metrics

### Grafana
- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: admin
- **Dashboards**: Pre-configured dashboards for system monitoring

### Key Metrics
- **Response Time**: API response times
- **Error Rate**: Error percentage
- **Memory Usage**: System memory consumption
- **CPU Usage**: CPU utilization
- **Request Rate**: Requests per second

## 🔍 Troubleshooting

### Common Issues

#### Service Not Starting
```bash
# Check logs
docker-compose logs scirag-api

# Check health
curl http://localhost:8000/health

# Restart service
docker-compose restart scirag-api
```

#### High Memory Usage
```bash
# Check memory usage
docker stats

# Adjust memory limits in docker-compose.yml
# Restart services
docker-compose restart
```

#### API Errors
```bash
# Check API logs
docker-compose logs -f scirag-api

# Test endpoints
python scripts/test_production.py
```

### Log Files
- **API Logs**: `./logs/scirag.log`
- **Docker Logs**: `docker-compose logs`
- **System Logs**: `/var/log/syslog`

## 🔒 Security

### Authentication
```bash
# Enable authentication
SCIRAG_ENABLE_AUTH=true
SCIRAG_AUTH_TOKEN=your-secure-token
```

### CORS Configuration
```bash
# Configure CORS
SCIRAG_CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Rate Limiting
```bash
# Enable rate limiting
SCIRAG_ENABLE_RATE_LIMITING=true
SCIRAG_RATE_LIMIT_REQUESTS=100
SCIRAG_RATE_LIMIT_WINDOW=3600
```

### SSL/TLS
```bash
# Enable SSL
SCIRAG_ENABLE_SSL=true
SCIRAG_SSL_CERT_PATH=/path/to/cert.pem
SCIRAG_SSL_KEY_PATH=/path/to/key.pem
```

## 📈 Performance Optimization

### Scaling
```bash
# Scale API workers
SCIRAG_API_WORKERS=8

# Scale with Docker Compose
docker-compose up -d --scale scirag-api=3
```

### Caching
```bash
# Enable caching
SCIRAG_ENABLE_CACHING=true
SCIRAG_CACHE_SIZE=1000
SCIRAG_CACHE_TTL=3600
```

### Database Optimization
```bash
# Use PostgreSQL for production
SCIRAG_DATABASE_URL=postgresql://user:pass@localhost/scirag
```

## 🚀 Deployment Strategies

### Docker Compose (Recommended)
```bash
# Production deployment
./scripts/deploy.sh production

# Development deployment
./scripts/deploy.sh development
```

### Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment
kubectl get pods
kubectl get services
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python -m scirag.api.server
```

## 📝 Maintenance

### Backup
```bash
# Backup data
tar -czf scirag-backup-$(date +%Y%m%d).tar.gz data/ logs/ cache/

# Backup database
sqlite3 data/scirag.db ".backup backup.db"
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Monitoring
```bash
# Check system health
curl http://localhost:8000/health

# View metrics
curl http://localhost:8000/metrics

# Check logs
tail -f logs/scirag.log
```

## 📞 Support

### Documentation
- **API Docs**: http://localhost:8000/docs
- **Code Documentation**: `docs/`
- **Configuration Guide**: `CONFIG.md`

### Monitoring
- **Health Dashboard**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics
- **Grafana**: http://localhost:3000

### Logs
- **Application Logs**: `./logs/scirag.log`
- **Docker Logs**: `docker-compose logs`
- **System Logs**: `/var/log/syslog`

## 🎯 Best Practices

### Production Checklist
- [ ] Configure proper logging levels
- [ ] Set up monitoring and alerting
- [ ] Enable authentication and security
- [ ] Configure rate limiting
- [ ] Set up backup procedures
- [ ] Test disaster recovery
- [ ] Monitor performance metrics
- [ ] Regular security updates

### Performance Tips
- Use Redis for caching
- Enable compression
- Monitor memory usage
- Scale horizontally when needed
- Use connection pooling
- Optimize database queries

### Security Tips
- Use HTTPS in production
- Implement proper authentication
- Regular security audits
- Keep dependencies updated
- Monitor for vulnerabilities
- Use environment variables for secrets

---

**Enhanced SciRAG Production System** - Ready for enterprise deployment! 🚀
