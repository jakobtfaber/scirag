"""
Health checker for Enhanced SciRAG system.

This module provides comprehensive health checking functionality for the enhanced
SciRAG system, including component health, system resources, and performance monitoring.
"""

import time
import psutil
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from ..enhanced_processing import EnhancedDocumentProcessor, MathematicalProcessor, ContentClassifier
from ..enhanced_processing.monitoring import EnhancedProcessingMonitor


class SciRagHealthChecker:
    """Comprehensive health checker for Enhanced SciRAG system."""
    
    def __init__(self, monitoring_interval: int = 60):
        """
        Initialize health checker.
        
        Args:
            monitoring_interval: Monitoring interval in seconds
        """
        self.monitoring_interval = monitoring_interval
        self.logger = logging.getLogger(__name__)
        self.health_history = []
        self.component_status = {}
        self.last_check_time = None
        
        # Initialize monitoring components
        self.monitor = EnhancedProcessingMonitor()
        self.processor = EnhancedDocumentProcessor()
        self.math_processor = MathematicalProcessor()
        self.classifier = ContentClassifier()
    
    def run_health_checks(self) -> Dict[str, Any]:
        """
        Run comprehensive health checks.
        
        Returns:
            Health status dictionary
        """
        self.last_check_time = datetime.now()
        
        health_status = {
            'timestamp': self.last_check_time.isoformat(),
            'overall_status': 'healthy',
            'components': {},
            'system_resources': {},
            'performance_metrics': {},
            'errors': [],
            'warnings': []
        }
        
        # Check individual components
        self._check_enhanced_processing(health_status)
        self._check_mathematical_processing(health_status)
        self._check_content_classification(health_status)
        self._check_system_resources(health_status)
        self._check_performance_metrics(health_status)
        
        # Determine overall status
        health_status['overall_status'] = self._determine_overall_status(health_status)
        
        # Store health history
        self.health_history.append(health_status)
        if len(self.health_history) > 100:  # Keep last 100 checks
            self.health_history.pop(0)
        
        return health_status
    
    def _check_enhanced_processing(self, health_status: Dict[str, Any]):
        """Check enhanced processing component health."""
        try:
            # Test document processing with sample content
            test_content = "This is a test document with some content."
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(test_content)
                f.flush()
                
                try:
                    chunks = self.processor.process_document(Path(f.name), "health_check")
                    
                    health_status['components']['enhanced_processing'] = {
                        'status': 'healthy',
                        'chunks_processed': len(chunks),
                        'processing_time': 0.1,  # Placeholder
                        'error_count': 0
                    }
                finally:
                    os.unlink(f.name)
                    
        except Exception as e:
            health_status['components']['enhanced_processing'] = {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
            health_status['errors'].append(f"Enhanced processing error: {e}")
    
    def _check_mathematical_processing(self, health_status: Dict[str, Any]):
        """Check mathematical processing component health."""
        try:
            # Test equation processing
            test_equation = r"E = mc^2"
            result = self.math_processor.process_equation(test_equation)
            
            if result and 'equation_tex' in result:
                health_status['components']['mathematical_processing'] = {
                    'status': 'healthy',
                    'equations_processed': 1,
                    'processing_time': 0.05,  # Placeholder
                    'error_count': 0
                }
            else:
                health_status['components']['mathematical_processing'] = {
                    'status': 'unhealthy',
                    'error': 'Invalid processing result'
                }
                health_status['errors'].append("Mathematical processing returned invalid result")
                
        except Exception as e:
            health_status['components']['mathematical_processing'] = {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
            health_status['errors'].append(f"Mathematical processing error: {e}")
    
    def _check_content_classification(self, health_status: Dict[str, Any]):
        """Check content classification component health."""
        try:
            # Test content classification
            test_cases = [
                ("This is prose text.", "prose"),
                (r"\begin{equation} E = mc^2 \end{equation}", "equation"),
                (r"\begin{figure} \includegraphics{test.png} \end{figure}", "figure")
            ]
            
            correct_classifications = 0
            for content, expected_type in test_cases:
                result = self.classifier.classify_content(content, {})
                if result.value == expected_type:
                    correct_classifications += 1
            
            accuracy = correct_classifications / len(test_cases)
            
            health_status['components']['content_classification'] = {
                'status': 'healthy' if accuracy >= 0.8 else 'degraded',
                'accuracy': accuracy,
                'test_cases': len(test_cases),
                'correct_classifications': correct_classifications
            }
            
            if accuracy < 0.8:
                health_status['warnings'].append(f"Content classification accuracy low: {accuracy:.2f}")
                
        except Exception as e:
            health_status['components']['content_classification'] = {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
            health_status['errors'].append(f"Content classification error: {e}")
    
    def _check_system_resources(self, health_status: Dict[str, Any]):
        """Check system resource usage."""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_available = memory.available / (1024**3)  # GB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            disk_free = disk.free / (1024**3)  # GB
            
            health_status['system_resources'] = {
                'cpu_usage_percent': cpu_usage,
                'memory_usage_percent': memory_usage,
                'memory_available_gb': memory_available,
                'disk_usage_percent': disk_usage,
                'disk_free_gb': disk_free
            }
            
            # Check for resource warnings
            if cpu_usage > 80:
                health_status['warnings'].append(f"High CPU usage: {cpu_usage:.1f}%")
            
            if memory_usage > 80:
                health_status['warnings'].append(f"High memory usage: {memory_usage:.1f}%")
            
            if disk_usage > 90:
                health_status['warnings'].append(f"High disk usage: {disk_usage:.1f}%")
                
        except Exception as e:
            health_status['system_resources'] = {
                'status': 'error',
                'error': str(e)
            }
            health_status['errors'].append(f"System resource check error: {e}")
    
    def _check_performance_metrics(self, health_status: Dict[str, Any]):
        """Check performance metrics."""
        try:
            # Get metrics from monitoring system
            metrics = self.monitor.get_metrics()
            
            health_status['performance_metrics'] = {
                'avg_response_time': metrics.get('avg_response_time', 0),
                'max_response_time': metrics.get('max_response_time', 0),
                'error_rate': metrics.get('error_rate', 0),
                'success_count': metrics.get('success_count', 0),
                'error_count': metrics.get('error_count', 0)
            }
            
            # Check performance thresholds
            if metrics.get('error_rate', 0) > 0.1:  # 10% error rate
                health_status['warnings'].append(f"High error rate: {metrics.get('error_rate', 0):.2f}")
            
            if metrics.get('avg_response_time', 0) > 5.0:  # 5 seconds
                health_status['warnings'].append(f"High average response time: {metrics.get('avg_response_time', 0):.2f}s")
                
        except Exception as e:
            health_status['performance_metrics'] = {
                'status': 'error',
                'error': str(e)
            }
            health_status['errors'].append(f"Performance metrics check error: {e}")
    
    def _determine_overall_status(self, health_status: Dict[str, Any]) -> str:
        """Determine overall system health status."""
        if health_status['errors']:
            return 'unhealthy'
        
        # Check component status
        component_statuses = []
        for component, status in health_status['components'].items():
            if isinstance(status, dict) and 'status' in status:
                component_statuses.append(status['status'])
        
        if 'unhealthy' in component_statuses:
            return 'unhealthy'
        elif 'degraded' in component_statuses:
            return 'degraded'
        elif health_status['warnings']:
            return 'warning'
        else:
            return 'healthy'
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary from recent checks."""
        if not self.health_history:
            return {'status': 'no_data', 'message': 'No health checks performed'}
        
        recent_checks = self.health_history[-10:]  # Last 10 checks
        
        # Calculate summary statistics
        status_counts = {}
        for check in recent_checks:
            status = check['overall_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get latest check
        latest_check = recent_checks[-1]
        
        summary = {
            'latest_status': latest_check['overall_status'],
            'status_distribution': status_counts,
            'total_checks': len(recent_checks),
            'recent_errors': len(latest_check.get('errors', [])),
            'recent_warnings': len(latest_check.get('warnings', [])),
            'timestamp': latest_check['timestamp']
        }
        
        return summary
    
    def get_component_status(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get status of specific component."""
        if not self.health_history:
            return None
        
        latest_check = self.health_history[-1]
        return latest_check['components'].get(component_name)
    
    def get_system_resources(self) -> Optional[Dict[str, Any]]:
        """Get current system resource usage."""
        if not self.health_history:
            return None
        
        latest_check = self.health_history[-1]
        return latest_check.get('system_resources')
    
    def get_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current performance metrics."""
        if not self.health_history:
            return None
        
        latest_check = self.health_history[-1]
        return latest_check.get('performance_metrics')
    
    def export_health_report(self, format: str = 'json') -> str:
        """Export health report in specified format."""
        if format == 'json':
            import json
            return json.dumps(self.health_history, indent=2)
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['timestamp', 'overall_status', 'errors', 'warnings'])
            
            # Write data
            for check in self.health_history:
                writer.writerow([
                    check['timestamp'],
                    check['overall_status'],
                    len(check.get('errors', [])),
                    len(check.get('warnings', []))
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def check_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Check health trends over specified time period."""
        if not self.health_history:
            return {'status': 'no_data', 'message': 'No health checks performed'}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter checks within time period
        recent_checks = [
            check for check in self.health_history
            if datetime.fromisoformat(check['timestamp']) > cutoff_time
        ]
        
        if not recent_checks:
            return {'status': 'no_data', 'message': f'No health checks in last {hours} hours'}
        
        # Analyze trends
        status_trend = [check['overall_status'] for check in recent_checks]
        error_trend = [len(check.get('errors', [])) for check in recent_checks]
        warning_trend = [len(check.get('warnings', [])) for check in recent_checks]
        
        # Calculate trend indicators
        status_changes = sum(1 for i in range(1, len(status_trend)) if status_trend[i] != status_trend[i-1])
        avg_errors = sum(error_trend) / len(error_trend)
        avg_warnings = sum(warning_trend) / len(warning_trend)
        
        trends = {
            'time_period_hours': hours,
            'total_checks': len(recent_checks),
            'status_changes': status_changes,
            'average_errors': avg_errors,
            'average_warnings': avg_warnings,
            'current_status': status_trend[-1],
            'status_trend': status_trend,
            'error_trend': error_trend,
            'warning_trend': warning_trend
        }
        
        return trends


# Import tempfile for the health check
import tempfile
import os
