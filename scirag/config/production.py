"""
Production configuration for Enhanced SciRAG.

This module provides production-ready configuration settings for the enhanced
SciRAG system with RAGBook integration.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


class ProductionConfig:
    """Production configuration for Enhanced SciRAG."""
    
    def __init__(self):
        """Initialize production configuration."""
        self._load_environment_variables()
        self._setup_logging_config()
        self._setup_performance_config()
        self._setup_monitoring_config()
        self._setup_security_config()
    
    def _load_environment_variables(self):
        """Load configuration from environment variables."""
        # Core SciRAG settings
        self.corpus_name = os.getenv('SCIRAG_CORPUS_NAME', 'enhanced_scirag_corpus')
        self.markdown_files_path = os.getenv('SCIRAG_MARKDOWN_FILES_PATH', './markdown_files')
        self.gen_model = os.getenv('SCIRAG_GEN_MODEL', 'gemini-1.5-pro')
        
        # Enhanced processing settings
        self.enable_enhanced_processing = os.getenv('SCIRAG_ENHANCED_PROCESSING', 'true').lower() == 'true'
        self.enable_mathematical_processing = os.getenv('SCIRAG_MATH_PROCESSING', 'true').lower() == 'true'
        self.enable_asset_processing = os.getenv('SCIRAG_ASSET_PROCESSING', 'true').lower() == 'true'
        self.enable_glossary_extraction = os.getenv('SCIRAG_GLOSSARY_EXTRACTION', 'true').lower() == 'true'
        
        # Chunking settings
        self.chunk_size = int(os.getenv('SCIRAG_CHUNK_SIZE', '320'))
        self.overlap_ratio = float(os.getenv('SCIRAG_OVERLAP_RATIO', '0.12'))
        
        # Performance settings
        self.max_concurrent_requests = int(os.getenv('SCIRAG_MAX_CONCURRENT_REQUESTS', '10'))
        self.request_timeout = int(os.getenv('SCIRAG_REQUEST_TIMEOUT', '30'))
        self.cache_ttl = int(os.getenv('SCIRAG_CACHE_TTL', '3600'))  # 1 hour
        
        # API settings
        self.api_host = os.getenv('SCIRAG_API_HOST', '0.0.0.0')
        self.api_port = int(os.getenv('SCIRAG_API_PORT', '8000'))
        self.api_workers = int(os.getenv('SCIRAG_API_WORKERS', '4'))
        
        # Database settings
        self.database_url = os.getenv('SCIRAG_DATABASE_URL', 'sqlite:///scirag.db')
        self.redis_url = os.getenv('SCIRAG_REDIS_URL', 'redis://localhost:6379/0')
        
        # Logging settings
        self.log_level = os.getenv('SCIRAG_LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('SCIRAG_LOG_FILE', './logs/scirag.log')
        self.log_max_size = int(os.getenv('SCIRAG_LOG_MAX_SIZE', '10485760'))  # 10MB
        self.log_backup_count = int(os.getenv('SCIRAG_LOG_BACKUP_COUNT', '5'))
    
    def _setup_logging_config(self):
        """Setup logging configuration."""
        self.logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.log_level,
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': self.log_level,
                    'formatter': 'detailed',
                    'filename': self.log_file,
                    'maxBytes': self.log_max_size,
                    'backupCount': self.log_backup_count
                }
            },
            'loggers': {
                'scirag': {
                    'handlers': ['console', 'file'],
                    'level': self.log_level,
                    'propagate': False
                },
                'scirag.enhanced_processing': {
                    'handlers': ['console', 'file'],
                    'level': self.log_level,
                    'propagate': False
                },
                'scirag.validation': {
                    'handlers': ['console', 'file'],
                    'level': self.log_level,
                    'propagate': False
                }
            }
        }
    
    def _setup_performance_config(self):
        """Setup performance configuration."""
        self.performance_config = {
            'max_memory_usage': int(os.getenv('SCIRAG_MAX_MEMORY_USAGE', '2048')),  # MB
            'max_cpu_usage': int(os.getenv('SCIRAG_MAX_CPU_USAGE', '80')),  # Percentage
            'max_response_time': float(os.getenv('SCIRAG_MAX_RESPONSE_TIME', '5.0')),  # seconds
            'max_error_rate': float(os.getenv('SCIRAG_MAX_ERROR_RATE', '0.05')),  # 5%
            'enable_caching': os.getenv('SCIRAG_ENABLE_CACHING', 'true').lower() == 'true',
            'cache_size': int(os.getenv('SCIRAG_CACHE_SIZE', '1000')),
            'enable_compression': os.getenv('SCIRAG_ENABLE_COMPRESSION', 'true').lower() == 'true'
        }
    
    def _setup_monitoring_config(self):
        """Setup monitoring configuration."""
        self.monitoring_config = {
            'enable_metrics': os.getenv('SCIRAG_ENABLE_METRICS', 'true').lower() == 'true',
            'metrics_interval': int(os.getenv('SCIRAG_METRICS_INTERVAL', '60')),  # seconds
            'health_check_interval': int(os.getenv('SCIRAG_HEALTH_CHECK_INTERVAL', '30')),  # seconds
            'enable_alerting': os.getenv('SCIRAG_ENABLE_ALERTING', 'true').lower() == 'true',
            'alert_email': os.getenv('SCIRAG_ALERT_EMAIL', ''),
            'alert_webhook': os.getenv('SCIRAG_ALERT_WEBHOOK', ''),
            'enable_dashboard': os.getenv('SCIRAG_ENABLE_DASHBOARD', 'true').lower() == 'true',
            'dashboard_port': int(os.getenv('SCIRAG_DASHBOARD_PORT', '8080'))
        }
    
    def _setup_security_config(self):
        """Setup security configuration."""
        self.security_config = {
            'enable_auth': os.getenv('SCIRAG_ENABLE_AUTH', 'false').lower() == 'true',
            'auth_token': os.getenv('SCIRAG_AUTH_TOKEN', ''),
            'enable_cors': os.getenv('SCIRAG_ENABLE_CORS', 'true').lower() == 'true',
            'cors_origins': os.getenv('SCIRAG_CORS_ORIGINS', '*').split(','),
            'enable_rate_limiting': os.getenv('SCIRAG_ENABLE_RATE_LIMITING', 'true').lower() == 'true',
            'rate_limit_requests': int(os.getenv('SCIRAG_RATE_LIMIT_REQUESTS', '100')),
            'rate_limit_window': int(os.getenv('SCIRAG_RATE_LIMIT_WINDOW', '3600')),  # 1 hour
            'enable_ssl': os.getenv('SCIRAG_ENABLE_SSL', 'false').lower() == 'true',
            'ssl_cert_path': os.getenv('SCIRAG_SSL_CERT_PATH', ''),
            'ssl_key_path': os.getenv('SCIRAG_SSL_KEY_PATH', '')
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get complete configuration dictionary."""
        return {
            'core': {
                'corpus_name': self.corpus_name,
                'markdown_files_path': self.markdown_files_path,
                'gen_model': self.gen_model
            },
            'enhanced_processing': {
                'enabled': self.enable_enhanced_processing,
                'mathematical_processing': self.enable_mathematical_processing,
                'asset_processing': self.enable_asset_processing,
                'glossary_extraction': self.enable_glossary_extraction
            },
            'chunking': {
                'chunk_size': self.chunk_size,
                'overlap_ratio': self.overlap_ratio
            },
            'performance': self.performance_config,
            'monitoring': self.monitoring_config,
            'security': self.security_config,
            'logging': self.logging_config,
            'api': {
                'host': self.api_host,
                'port': self.api_port,
                'workers': self.api_workers
            },
            'database': {
                'url': self.database_url,
                'redis_url': self.redis_url
            }
        }
    
    def validate_config(self) -> bool:
        """Validate configuration settings."""
        errors = []
        
        # Validate required settings
        if not self.corpus_name:
            errors.append("Corpus name is required")
        
        if not Path(self.markdown_files_path).exists():
            errors.append(f"Markdown files path does not exist: {self.markdown_files_path}")
        
        # Validate performance settings
        if self.chunk_size <= 0:
            errors.append("Chunk size must be positive")
        
        if not 0 <= self.overlap_ratio <= 1:
            errors.append("Overlap ratio must be between 0 and 1")
        
        # Validate API settings
        if not 1 <= self.api_port <= 65535:
            errors.append("API port must be between 1 and 65535")
        
        if self.api_workers <= 0:
            errors.append("API workers must be positive")
        
        # Validate security settings
        if self.security_config['enable_auth'] and not self.security_config['auth_token']:
            errors.append("Auth token is required when authentication is enabled")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def create_directories(self):
        """Create necessary directories."""
        directories = [
            Path(self.markdown_files_path),
            Path(self.log_file).parent,
            Path('./data'),
            Path('./cache'),
            Path('./temp')
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def export_config(self, file_path: str):
        """Export configuration to file."""
        import json
        
        config = self.get_config()
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config_from_file(self, file_path: str):
        """Load configuration from file."""
        import json
        
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        # Update configuration from file
        if 'core' in config:
            self.corpus_name = config['core'].get('corpus_name', self.corpus_name)
            self.markdown_files_path = config['core'].get('markdown_files_path', self.markdown_files_path)
            self.gen_model = config['core'].get('gen_model', self.gen_model)
        
        if 'enhanced_processing' in config:
            self.enable_enhanced_processing = config['enhanced_processing'].get('enabled', self.enable_enhanced_processing)
            self.enable_mathematical_processing = config['enhanced_processing'].get('mathematical_processing', self.enable_mathematical_processing)
            self.enable_asset_processing = config['enhanced_processing'].get('asset_processing', self.enable_asset_processing)
            self.enable_glossary_extraction = config['enhanced_processing'].get('glossary_extraction', self.enable_glossary_extraction)
        
        if 'chunking' in config:
            self.chunk_size = config['chunking'].get('chunk_size', self.chunk_size)
            self.overlap_ratio = config['chunking'].get('overlap_ratio', self.overlap_ratio)


# Global configuration instance
config = ProductionConfig()
