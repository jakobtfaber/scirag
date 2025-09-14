#!/usr/bin/env python3
"""
Simple Production Test

This script tests the production configuration and deployment files
without complex imports that might cause dependency issues.
"""

import sys
import os
from pathlib import Path

def test_production_files():
    """Test production files exist and are properly configured."""
    print("🧪 Testing production files...")
    
    try:
        # Check if production files exist
        files_to_check = [
            "Dockerfile",
            "docker-compose.yml", 
            "requirements.txt",
            "PRODUCTION_GUIDE.md",
            "scirag/config/production.py",
            "scirag/api/server.py",
            "scripts/deploy.sh",
            "scripts/test_production.py",
            "monitoring/prometheus.yml",
            "monitoring/grafana/datasources/prometheus.yml"
        ]
        
        missing_files = []
        for file_path in files_to_check:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing files: {missing_files}")
            return False
        
        print("✅ All production files found")
        return True
        
    except Exception as e:
        print(f"❌ Production files test failed: {e}")
        return False

def test_docker_configuration():
    """Test Docker configuration."""
    print("🧪 Testing Docker configuration...")
    
    try:
        # Check Dockerfile
        with open("Dockerfile", "r") as f:
            dockerfile_content = f.read()
        
        assert "FROM python:3.12-slim" in dockerfile_content
        assert "WORKDIR /app" in dockerfile_content
        assert "EXPOSE 8000" in dockerfile_content
        assert "HEALTHCHECK" in dockerfile_content
        
        print("✅ Dockerfile configuration is correct")
        
        # Check docker-compose.yml
        with open("docker-compose.yml", "r") as f:
            compose_content = f.read()
        
        assert "scirag-api:" in compose_content
        assert "redis:" in compose_content
        assert "nginx:" in compose_content
        assert "monitoring:" in compose_content
        assert "grafana:" in compose_content
        
        print("✅ Docker Compose configuration is correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Docker configuration test failed: {e}")
        return False

def test_requirements_file():
    """Test requirements file."""
    print("🧪 Testing requirements file...")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements_content = f.read()
        
        # Check for key dependencies
        required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "langchain",
            "openai",
            "google-generativeai",
            "sympy",
            "redis",
            "prometheus-client"
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in requirements_content:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {missing_packages}")
            return False
        
        print("✅ Requirements file contains all necessary packages")
        return True
        
    except Exception as e:
        print(f"❌ Requirements file test failed: {e}")
        return False

def test_script_permissions():
    """Test script permissions."""
    print("🧪 Testing script permissions...")
    
    try:
        scripts = [
            "scripts/deploy.sh",
            "scripts/test_production.py"
        ]
        
        for script in scripts:
            if not os.access(script, os.X_OK):
                print(f"❌ Script {script} is not executable")
                return False
        
        print("✅ All scripts are executable")
        return True
        
    except Exception as e:
        print(f"❌ Script permissions test failed: {e}")
        return False

def test_production_config_structure():
    """Test production configuration structure."""
    print("🧪 Testing production configuration structure...")
    
    try:
        with open("scirag/config/production.py", "r") as f:
            config_content = f.read()
        
        # Check for key configuration elements
        config_elements = [
            "class ProductionConfig",
            "def _load_environment_variables",
            "def _setup_logging_config",
            "def _setup_performance_config",
            "def _setup_monitoring_config",
            "def _setup_security_config",
            "def get_config",
            "def validate_config"
        ]
        
        missing_elements = []
        for element in config_elements:
            if element not in config_content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing configuration elements: {missing_elements}")
            return False
        
        print("✅ Production configuration structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ Production configuration structure test failed: {e}")
        return False

def test_api_server_structure():
    """Test API server structure."""
    print("🧪 Testing API server structure...")
    
    try:
        with open("scirag/api/server.py", "r") as f:
            server_content = f.read()
        
        # Check for key API elements
        api_elements = [
            "class QueryRequest",
            "class QueryResponse",
            "class DocumentUploadRequest",
            "class DocumentUploadResponse",
            "class HealthResponse",
            "class MetricsResponse",
            "app = FastAPI",
            "@app.get",
            "@app.post",
            "def run_server"
        ]
        
        missing_elements = []
        for element in api_elements:
            if element not in server_content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing API elements: {missing_elements}")
            return False
        
        print("✅ API server structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ API server structure test failed: {e}")
        return False

def test_monitoring_configuration():
    """Test monitoring configuration."""
    print("🧪 Testing monitoring configuration...")
    
    try:
        # Check Prometheus config
        with open("monitoring/prometheus.yml", "r") as f:
            prometheus_content = f.read()
        
        assert "scirag-api:" in prometheus_content
        assert "redis:" in prometheus_content
        assert "scrape_configs:" in prometheus_content
        
        print("✅ Prometheus configuration is correct")
        
        # Check Grafana config
        with open("monitoring/grafana/datasources/prometheus.yml", "r") as f:
            grafana_content = f.read()
        
        assert "Prometheus" in grafana_content
        assert "prometheus" in grafana_content
        
        print("✅ Grafana configuration is correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring configuration test failed: {e}")
        return False

def main():
    """Run all production tests."""
    print("🚀 Starting Simple Production Tests")
    print("=" * 50)
    
    tests = [
        test_production_files,
        test_docker_configuration,
        test_requirements_file,
        test_script_permissions,
        test_production_config_structure,
        test_api_server_structure,
        test_monitoring_configuration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if failed == 0:
        print("🎉 All production tests passed!")
        print("✅ Enhanced SciRAG production setup is complete!")
        print("🚀 Ready for deployment!")
    else:
        print(f"⚠️  {failed} tests failed. Please review and fix issues.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
