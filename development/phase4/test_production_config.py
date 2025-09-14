#!/usr/bin/env python3
"""
Test Production Configuration

This script tests the production configuration without importing the main scirag package
to avoid dependency issues.
"""

import sys
import os
from pathlib import Path

# Add the scirag directory to the path
sys.path.insert(0, str(Path(__file__).parent / "scirag"))

def test_production_config():
    """Test production configuration."""
    print("🧪 Testing production configuration...")
    
    try:
        # Import production config directly
        from scirag.config.production import ProductionConfig
        
        # Create config instance
        config = ProductionConfig()
        
        # Test basic configuration
        assert config.enable_enhanced_processing == True
        assert config.enable_mathematical_processing == True
        assert config.enable_asset_processing == True
        assert config.enable_glossary_extraction == True
        assert config.api_port == 8000
        assert config.chunk_size == 320
        assert config.overlap_ratio == 0.12
        
        print("✅ Production configuration loaded successfully")
        print(f"  - Enhanced processing: {config.enable_enhanced_processing}")
        print(f"  - Mathematical processing: {config.enable_mathematical_processing}")
        print(f"  - Asset processing: {config.enable_asset_processing}")
        print(f"  - Glossary extraction: {config.enable_glossary_extraction}")
        print(f"  - API port: {config.api_port}")
        print(f"  - Chunk size: {config.chunk_size}")
        print(f"  - Overlap ratio: {config.overlap_ratio}")
        
        # Test configuration validation
        is_valid = config.validate_config()
        print(f"  - Configuration valid: {is_valid}")
        
        # Test configuration export
        config_dict = config.get_config()
        assert 'core' in config_dict
        assert 'enhanced_processing' in config_dict
        assert 'performance' in config_dict
        assert 'monitoring' in config_dict
        assert 'security' in config_dict
        
        print("✅ Configuration structure is correct")
        
        # Test directory creation
        config.create_directories()
        print("✅ Directories created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Production configuration test failed: {e}")
        return False

def test_api_server_import():
    """Test API server import."""
    print("🧪 Testing API server import...")
    
    try:
        # Test if we can import the API server components
        from scirag.api.server import app, ProductionConfig
        
        print("✅ API server components imported successfully")
        print(f"  - FastAPI app: {app}")
        print(f"  - App title: {app.title}")
        print(f"  - App version: {app.version}")
        
        return True
        
    except Exception as e:
        print(f"❌ API server import test failed: {e}")
        return False

def test_docker_config():
    """Test Docker configuration."""
    print("🧪 Testing Docker configuration...")
    
    try:
        # Check if Docker files exist
        dockerfile_path = Path("Dockerfile")
        compose_path = Path("docker-compose.yml")
        
        assert dockerfile_path.exists(), "Dockerfile not found"
        assert compose_path.exists(), "docker-compose.yml not found"
        
        print("✅ Docker configuration files found")
        
        # Check if requirements.txt exists
        requirements_path = Path("requirements.txt")
        assert requirements_path.exists(), "requirements.txt not found"
        
        print("✅ Requirements file found")
        
        return True
        
    except Exception as e:
        print(f"❌ Docker configuration test failed: {e}")
        return False

def test_deployment_scripts():
    """Test deployment scripts."""
    print("🧪 Testing deployment scripts...")
    
    try:
        # Check if deployment scripts exist and are executable
        deploy_script = Path("scripts/deploy.sh")
        test_script = Path("scripts/test_production.py")
        
        assert deploy_script.exists(), "deploy.sh not found"
        assert test_script.exists(), "test_production.py not found"
        
        # Check if scripts are executable
        assert os.access(deploy_script, os.X_OK), "deploy.sh not executable"
        assert os.access(test_script, os.X_OK), "test_production.py not executable"
        
        print("✅ Deployment scripts found and executable")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment scripts test failed: {e}")
        return False

def main():
    """Run all production tests."""
    print("🚀 Starting Production Configuration Tests")
    print("=" * 50)
    
    tests = [
        test_production_config,
        test_api_server_import,
        test_docker_config,
        test_deployment_scripts
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
        print("🎉 All production configuration tests passed!")
        print("✅ Enhanced SciRAG is ready for production deployment!")
    else:
        print(f"⚠️  {failed} tests failed. Please review and fix issues.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
