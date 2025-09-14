"""
Tests for Enhanced Processing Configuration.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the scirag module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scirag.config import EnhancedProcessingConfig


class TestEnhancedProcessingConfig:
    """Test cases for EnhancedProcessingConfig."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Clear any existing environment variables
        self.original_env = {}
        for key in os.environ:
            if key.startswith('SCIRAG_'):
                self.original_env[key] = os.environ[key]
                del os.environ[key]
    
    def teardown_method(self):
        """Clean up after tests."""
        # Restore original environment variables
        for key, value in self.original_env.items():
            os.environ[key] = value
    
    def test_default_configuration(self):
        """Test default configuration values."""
        config = EnhancedProcessingConfig()
        
        # Test feature flags (should be False by default)
        assert config.ENABLE_ENHANCED_PROCESSING == False
        assert config.ENABLE_MATHEMATICAL_PROCESSING == True
        assert config.ENABLE_ASSET_PROCESSING == True
        assert config.ENABLE_GLOSSARY_EXTRACTION == True
        assert config.ENABLE_ENHANCED_CHUNKING == True
        
        # Test fallback settings
        assert config.FALLBACK_ON_ERROR == True
        assert config.LOG_ENHANCED_PROCESSING == True
        
        # Test performance thresholds
        assert config.MAX_PROCESSING_TIME == 30.0
        assert config.MEMORY_LIMIT_MB == 1024
        assert config.MAX_ERRORS_BEFORE_FALLBACK == 10
        
        # Test RAGBook settings
        assert config.RAGBOOK_CHUNK_SIZE == 320
        assert config.RAGBOOK_OVERLAP_RATIO == 0.12
        assert config.RAGBOOK_ENABLE_SYMPY == True
        assert config.RAGBOOK_ENABLE_OCR == True
    
    def test_environment_variable_override(self):
        """Test configuration override via environment variables."""
        # Set environment variables
        os.environ['SCIRAG_ENHANCED_PROCESSING'] = 'true'
        os.environ['SCIRAG_MATH_PROCESSING'] = 'false'
        os.environ['SCIRAG_CHUNK_SIZE'] = '500'
        os.environ['SCIRAG_OVERLAP_RATIO'] = '0.2'
        os.environ['SCIRAG_MAX_PROCESSING_TIME'] = '60.0'
        
        config = EnhancedProcessingConfig()
        
        assert config.ENABLE_ENHANCED_PROCESSING == True
        assert config.ENABLE_MATHEMATICAL_PROCESSING == False
        assert config.RAGBOOK_CHUNK_SIZE == 500
        assert config.RAGBOOK_OVERLAP_RATIO == 0.2
        assert config.MAX_PROCESSING_TIME == 60.0
    
    def test_get_config_dict(self):
        """Test configuration dictionary generation."""
        config = EnhancedProcessingConfig()
        config_dict = config.get_config_dict()
        
        # Test that all expected keys are present
        expected_keys = [
            'enhanced_processing', 'mathematical_processing', 'asset_processing',
            'glossary_extraction', 'enhanced_chunking', 'fallback_on_error',
            'log_enhanced_processing', 'max_processing_time', 'memory_limit_mb',
            'max_errors_before_fallback', 'chunk_size', 'overlap_ratio',
            'enable_sympy', 'enable_ocr', 'classification_threshold',
            'equation_threshold', 'figure_threshold', 'table_threshold',
            'glossary_threshold', 'math_kgram_size', 'math_max_variables',
            'math_max_operators', 'chunk_overlap_sentences', 'preserve_math_context',
            'preserve_asset_context', 'enable_performance_monitoring',
            'enable_health_checks', 'enable_auto_rollback', 'rollback_error_threshold',
            'rollback_time_window'
        ]
        
        for key in expected_keys:
            assert key in config_dict
        
        # Test some specific values
        assert config_dict['enhanced_processing'] == False
        assert config_dict['mathematical_processing'] == True
        assert config_dict['chunk_size'] == 320
        assert config_dict['overlap_ratio'] == 0.12
    
    def test_config_validation_valid(self):
        """Test configuration validation with valid values."""
        config = EnhancedProcessingConfig()
        errors = config.validate_config()
        
        # Should have no errors with default valid configuration
        assert len(errors) == 0
    
    def test_config_validation_invalid(self):
        """Test configuration validation with invalid values."""
        # Set invalid values via environment variables
        os.environ['SCIRAG_MAX_PROCESSING_TIME'] = '-1'
        os.environ['SCIRAG_MEMORY_LIMIT_MB'] = '0'
        os.environ['SCIRAG_OVERLAP_RATIO'] = '1.5'
        os.environ['SCIRAG_CLASSIFICATION_THRESHOLD'] = '2.0'
        os.environ['SCIRAG_MATH_KGRAM_SIZE'] = '0'
        os.environ['SCIRAG_MAX_ERRORS'] = '-5'
        
        config = EnhancedProcessingConfig()
        errors = config.validate_config()
        
        # Should have multiple errors
        assert len(errors) > 0
        
        # Check specific error messages
        error_messages = [error.lower() for error in errors]
        assert any('max_processing_time must be positive' in msg for msg in error_messages)
        assert any('memory_limit_mb must be positive' in msg for msg in error_messages)
        assert any('overlap_ratio must be between 0 and 1' in msg for msg in error_messages)
        assert any('classification_threshold must be between 0 and 1' in msg for msg in error_messages)
        assert any('math_kgram_size must be positive' in msg for msg in error_messages)
        assert any('max_errors_before_fallback must be positive' in msg for msg in error_messages)
    
    def test_boolean_environment_variables(self):
        """Test boolean environment variable parsing."""
        # Test various boolean representations
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('1', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
            ('', False),  # Empty string should default to False
            ('invalid', False)  # Invalid string should default to False
        ]
        
        for env_value, expected in test_cases:
            os.environ['SCIRAG_ENHANCED_PROCESSING'] = env_value
            config = EnhancedProcessingConfig()
            assert config.ENABLE_ENHANCED_PROCESSING == expected
    
    def test_numeric_environment_variables(self):
        """Test numeric environment variable parsing."""
        # Test integer parsing
        os.environ['SCIRAG_CHUNK_SIZE'] = '500'
        os.environ['SCIRAG_MEMORY_LIMIT_MB'] = '2048'
        os.environ['SCIRAG_MATH_KGRAM_SIZE'] = '5'
        
        config = EnhancedProcessingConfig()
        assert config.RAGBOOK_CHUNK_SIZE == 500
        assert config.MEMORY_LIMIT_MB == 2048
        assert config.MATH_KGRAM_SIZE == 5
        
        # Test float parsing
        os.environ['SCIRAG_OVERLAP_RATIO'] = '0.25'
        os.environ['SCIRAG_MAX_PROCESSING_TIME'] = '45.5'
        os.environ['SCIRAG_CLASSIFICATION_THRESHOLD'] = '0.7'
        
        config = EnhancedProcessingConfig()
        assert config.RAGBOOK_OVERLAP_RATIO == 0.25
        assert config.MAX_PROCESSING_TIME == 45.5
        assert config.CLASSIFICATION_CONFIDENCE_THRESHOLD == 0.7
    
    def test_configuration_immutability(self):
        """Test that configuration values are properly set."""
        config = EnhancedProcessingConfig()
        
        # Test that values are properly typed
        assert isinstance(config.ENABLE_ENHANCED_PROCESSING, bool)
        assert isinstance(config.ENABLE_MATHEMATICAL_PROCESSING, bool)
        assert isinstance(config.RAGBOOK_CHUNK_SIZE, int)
        assert isinstance(config.RAGBOOK_OVERLAP_RATIO, float)
        assert isinstance(config.MAX_PROCESSING_TIME, float)
        assert isinstance(config.MEMORY_LIMIT_MB, int)
    
    def test_classification_thresholds(self):
        """Test classification threshold configuration."""
        config = EnhancedProcessingConfig()
        
        # Test that all thresholds are between 0 and 1
        assert 0 <= config.CLASSIFICATION_CONFIDENCE_THRESHOLD <= 1
        assert 0 <= config.EQUATION_CONFIDENCE_THRESHOLD <= 1
        assert 0 <= config.FIGURE_CONFIDENCE_THRESHOLD <= 1
        assert 0 <= config.TABLE_CONFIDENCE_THRESHOLD <= 1
        assert 0 <= config.GLOSSARY_CONFIDENCE_THRESHOLD <= 1
        
        # Test that thresholds are reasonable
        assert config.EQUATION_CONFIDENCE_THRESHOLD >= 0.5
        assert config.FIGURE_CONFIDENCE_THRESHOLD >= 0.4
        assert config.TABLE_CONFIDENCE_THRESHOLD >= 0.4
        assert config.GLOSSARY_CONFIDENCE_THRESHOLD >= 0.5
    
    def test_ragbook_specific_settings(self):
        """Test RAGBook-specific configuration settings."""
        config = EnhancedProcessingConfig()
        
        # Test chunk size is reasonable
        assert 100 <= config.RAGBOOK_CHUNK_SIZE <= 2000
        
        # Test overlap ratio is reasonable
        assert 0.0 <= config.RAGBOOK_OVERLAP_RATIO <= 0.5
        
        # Test boolean settings
        assert isinstance(config.RAGBOOK_ENABLE_SYMPY, bool)
        assert isinstance(config.RAGBOOK_ENABLE_OCR, bool)
    
    def test_monitoring_settings(self):
        """Test monitoring and rollback configuration."""
        config = EnhancedProcessingConfig()
        
        # Test boolean settings
        assert isinstance(config.ENABLE_PERFORMANCE_MONITORING, bool)
        assert isinstance(config.ENABLE_HEALTH_CHECKS, bool)
        assert isinstance(config.ENABLE_AUTO_ROLLBACK, bool)
        
        # Test rollback settings
        assert 0 <= config.ROLLBACK_ERROR_THRESHOLD <= 1
        assert config.ROLLBACK_TIME_WINDOW > 0
    
    def test_mathematical_processing_settings(self):
        """Test mathematical processing configuration."""
        config = EnhancedProcessingConfig()
        
        # Test k-gram size
        assert 1 <= config.MATH_KGRAM_SIZE <= 10
        
        # Test max variables and operators
        assert config.MATH_MAX_VARIABLES > 0
        assert config.MATH_MAX_OPERATORS > 0
        
        # Test chunking settings
        assert config.CHUNK_OVERLAP_SENTENCES >= 0
        assert isinstance(config.PRESERVE_MATH_CONTEXT, bool)
        assert isinstance(config.PRESERVE_ASSET_CONTEXT, bool)


if __name__ == "__main__":
    pytest.main([__file__])
