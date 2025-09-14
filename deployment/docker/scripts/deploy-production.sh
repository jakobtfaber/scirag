#!/bin/bash

# Full-Scale Enhanced SciRAG Production Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="enhanced-scirag-production"
DOCKER_COMPOSE_FILE="deployment/docker/docker-compose.production.yml"
ENVIRONMENT=${1:-production}

echo -e "${BLUE}🚀 Starting Full-Scale Enhanced SciRAG Production Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Determine which compose command to use
if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"


# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p logs data cache temp markdown_files
mkdir -p deployment/docker/grafana/datasources
mkdir -p deployment/docker/grafana/dashboards
echo -e "${GREEN}✅ Directories created${NC}"

# Copy requirements file
echo -e "${YELLOW}Setting up requirements...${NC}"
cp deployment/docker/requirements.production.txt requirements.txt
echo -e "${GREEN}✅ Requirements file ready${NC}"

# Build and start services
echo -e "${YELLOW}Building Docker images...${NC}"
$COMPOSE_CMD -f $DOCKER_COMPOSE_FILE build --no-cache

echo -e "${YELLOW}Starting services...${NC}"
$COMPOSE_CMD -f $DOCKER_COMPOSE_FILE up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"

# Check SciRAG API
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ SciRAG API is healthy${NC}"
else
    echo -e "${RED}❌ SciRAG API health check failed${NC}"
fi

# Check Prometheus
if curl -f http://localhost:9090/-/healthy >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus is healthy${NC}"
else
    echo -e "${RED}❌ Prometheus health check failed${NC}"
fi

# Check Grafana
if curl -f http://localhost:3000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana is healthy${NC}"
else
    echo -e "${RED}❌ Grafana health check failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Full-Scale Enhanced SciRAG Production Deployment Complete!${NC}"
echo ""
echo -e "${BLUE}📊 Service URLs:${NC}"
echo -e "  • SciRAG API: http://localhost:8000"
echo -e "  • API Documentation: http://localhost:8000/docs"
echo -e "  • Health Check: http://localhost:8000/health"
echo -e "  • Metrics: http://localhost:8000/metrics"
echo -e "  • Prometheus: http://localhost:9090"
echo -e "  • Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo -e "  • View logs: $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE logs -f"
echo -e "  • Stop services: $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE down"
echo -e "  • Restart services: $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE restart"
echo -e "  • View status: $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE ps"
echo ""
echo -e "${BLUE}🧪 Test the API:${NC}"
echo -e "  curl -X POST http://localhost:8000/api/v2/process-document \\"
echo -e "    -H 'Content-Type: application/json' \\"
echo -e "    -d '{\"content\": \"E = mc^2\", \"content_type\": \"equation\"}'"
echo ""
echo -e "${GREEN}Ready for production use! 🚀${NC}"
