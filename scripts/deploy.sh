#!/bin/bash

# Enhanced SciRAG Production Deployment Script
# This script handles the complete deployment of the enhanced SciRAG system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="enhanced-scirag"
DOCKER_COMPOSE_FILE="deployment/docker/docker-compose.ultra-minimal.yml"
ENVIRONMENT=${1:-production}

echo -e "${BLUE}🚀 Starting Enhanced SciRAG Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed (V1 or V2)
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Set compose command
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    # Check if required files exist
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        print_error "Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    echo -e "${BLUE}Creating necessary directories...${NC}"
    
    mkdir -p markdown_files
    mkdir -p data
    mkdir -p logs
    mkdir -p cache
    mkdir -p temp
    mkdir -p ssl
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    
    print_status "Directories created"
}

# Build Docker images
build_images() {
    echo -e "${BLUE}Building Docker images...${NC}"
    
    $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE build --no-cache
    
    print_status "Docker images built successfully"
}

# Deploy services
deploy_services() {
    echo -e "${BLUE}Deploying services...${NC}"
    
    # Stop existing services
    $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE down
    
    # Start services
    $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE up -d
    
    print_status "Services deployed successfully"
}

# Wait for services to be ready
wait_for_services() {
    echo -e "${BLUE}Waiting for services to be ready...${NC}"
    
    # Wait for Redis
    echo "Waiting for Redis..."
    until $COMPOSE_CMD -f $DOCKER_COMPOSE_FILE exec redis redis-cli ping; do
        sleep 2
    done
    print_status "Redis is ready"
    
    # Wait for API
    echo "Waiting for API..."
    until curl -f http://localhost:8000/health > /dev/null 2>&1; do
        sleep 5
    done
    print_status "API is ready"
    
    # Wait for monitoring
    echo "Waiting for monitoring services..."
    sleep 10
    print_status "Monitoring services are ready"
}

# Run health checks
run_health_checks() {
    echo -e "${BLUE}Running health checks...${NC}"
    
    # Check API health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "API health check passed"
    else
        print_error "API health check failed"
        exit 1
    fi
    
    # Check metrics endpoint
    if curl -f http://localhost:8000/metrics > /dev/null 2>&1; then
        print_status "Metrics endpoint check passed"
    else
        print_error "Metrics endpoint check failed"
        exit 1
    fi
    
    print_status "All health checks passed"
}

# Display deployment information
display_info() {
    echo -e "${BLUE}Deployment Information${NC}"
    echo "=================================================="
    echo -e "${GREEN}✅ Enhanced SciRAG is now running!${NC}"
    echo ""
    echo "🌐 API Endpoints:"
    echo "  - Main API: http://localhost:8000"
    echo "  - Health Check: http://localhost:8000/health"
    echo "  - Metrics: http://localhost:8000/metrics"
    echo "  - API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📊 Monitoring:"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3000 (admin/admin)"
    echo ""
    echo "🔧 Management:"
    echo "  - View logs: $COMPOSE_CMD logs -f"
    echo "  - Stop services: $COMPOSE_CMD down"
    echo "  - Restart services: $COMPOSE_CMD restart"
    echo ""
    echo "📁 Data directories:"
    echo "  - Markdown files: ./markdown_files"
    echo "  - Logs: ./logs"
    echo "  - Data: ./data"
    echo "  - Cache: ./cache"
}

# Main deployment function
main() {
    check_prerequisites
    create_directories
    build_images
    deploy_services
    wait_for_services
    run_health_checks
    display_info
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
}

# Run main function
main "$@"
