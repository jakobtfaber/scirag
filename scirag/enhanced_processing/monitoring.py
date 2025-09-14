"""
Monitoring module for Enhanced SciRAG.

This module provides comprehensive monitoring capabilities for the enhanced
processing system including performance metrics, error tracking, and health checks.
"""

import time
import psutil
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque


class EnhancedProcessingMonitor:
    """Enhanced processing monitor for performance and health tracking."""
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize enhanced processing monitor.
        
        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.success_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=max_history)
        self.error_history = deque(maxlen=max_history)
        self.memory_usage = deque(maxlen=max_history)
        self.cpu_usage = deque(maxlen=max_history)
        
        # Performance thresholds
        self.thresholds = {
            'max_response_time': 5.0,  # seconds
            'max_error_rate': 0.1,     # 10%
            'max_memory_usage': 80.0,  # 80%
            'max_cpu_usage': 80.0      # 80%
        }
        
        # Component health
        self.component_health = {}
        
        # Start time for uptime calculation
        self.start_time = time.time()
    
    def record_success(self, operation: str, response_time: float):
        """
        Record successful operation.
        
        Args:
            operation: Operation name
            response_time: Response time in seconds
        """
        self.success_count += 1
        self.response_times.append(response_time)
        
        # Log success
        self.logger.debug(f"Operation '{operation}' completed in {response_time:.3f}s")
    
    def record_error(self, operation: str, error_message: str):
        """
        Record failed operation.
        
        Args:
            operation: Operation name
            error_message: Error message
        """
        self.error_count += 1
        self.error_history.append({
            'operation': operation,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Log error
        self.logger.error(f"Operation '{operation}' failed: {error_message}")
    
    def record_memory_usage(self):
        """Record current memory usage."""
        try:
            memory_percent = psutil.virtual_memory().percent
            self.memory_usage.append({
                'timestamp': datetime.now().isoformat(),
                'usage_percent': memory_percent
            })
        except Exception as e:
            self.logger.warning(f"Failed to record memory usage: {e}")
    
    def record_cpu_usage(self):
        """Record current CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.append({
                'timestamp': datetime.now().isoformat(),
                'usage_percent': cpu_percent
            })
        except Exception as e:
            self.logger.warning(f"Failed to record CPU usage: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
            Dictionary containing current metrics
        """
        total_operations = self.success_count + self.error_count
        error_rate = self.error_count / total_operations if total_operations > 0 else 0.0
        
        # Calculate response time statistics
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            max_response_time = max(self.response_times)
            min_response_time = min(self.response_times)
        else:
            avg_response_time = 0.0
            max_response_time = 0.0
            min_response_time = 0.0
        
        # Calculate uptime
        uptime = time.time() - self.start_time
        
        return {
            'success_count': self.success_count,
            'error_count': self.error_count,
            'total_operations': total_operations,
            'error_rate': error_rate,
            'avg_response_time': avg_response_time,
            'max_response_time': max_response_time,
            'min_response_time': min_response_time,
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'thresholds': self.thresholds.copy()
        }
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check system health.
        
        Returns:
            Dictionary containing health status
        """
        metrics = self.get_metrics()
        
        # Check thresholds
        health_issues = []
        
        if metrics['avg_response_time'] > self.thresholds['max_response_time']:
            health_issues.append(f"High average response time: {metrics['avg_response_time']:.2f}s")
        
        if metrics['error_rate'] > self.thresholds['max_error_rate']:
            health_issues.append(f"High error rate: {metrics['error_rate']:.2%}")
        
        # Check recent memory usage
        if self.memory_usage:
            recent_memory = self.memory_usage[-1]['usage_percent']
            if recent_memory > self.thresholds['max_memory_usage']:
                health_issues.append(f"High memory usage: {recent_memory:.1f}%")
        
        # Check recent CPU usage
        if self.cpu_usage:
            recent_cpu = self.cpu_usage[-1]['usage_percent']
            if recent_cpu > self.thresholds['max_cpu_usage']:
                health_issues.append(f"High CPU usage: {recent_cpu:.1f}%")
        
        # Determine overall health status
        if health_issues:
            status = 'unhealthy'
        elif metrics['error_rate'] > 0.05:  # 5% error rate
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'health_issues': health_issues,
            'component_health': self.component_health.copy()
        }
    
    def set_component_health(self, component: str, status: str, details: Optional[Dict[str, Any]] = None):
        """
        Set health status for a component.
        
        Args:
            component: Component name
            status: Health status ('healthy', 'degraded', 'unhealthy')
            details: Additional details about component health
        """
        self.component_health[component] = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
    
    def get_component_health(self, component: str) -> Optional[Dict[str, Any]]:
        """
        Get health status for a component.
        
        Args:
            component: Component name
            
        Returns:
            Component health status or None if not found
        """
        return self.component_health.get(component)
    
    def get_error_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent error history.
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of recent errors
        """
        return list(self.error_history)[-limit:]
    
    def get_performance_history(self, hours: int = 24) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get performance history for specified time period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary containing performance history
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter response times
        recent_response_times = []
        for i, response_time in enumerate(self.response_times):
            # Since we don't store timestamps for response times, we'll use index as proxy
            # In a real implementation, you'd store timestamps with each metric
            recent_response_times.append({
                'timestamp': datetime.now().isoformat(),  # Placeholder
                'response_time': response_time
            })
        
        # Filter memory usage
        recent_memory = [
            entry for entry in self.memory_usage
            if datetime.fromisoformat(entry['timestamp']) > cutoff_time
        ]
        
        # Filter CPU usage
        recent_cpu = [
            entry for entry in self.cpu_usage
            if datetime.fromisoformat(entry['timestamp']) > cutoff_time
        ]
        
        return {
            'response_times': recent_response_times,
            'memory_usage': recent_memory,
            'cpu_usage': recent_cpu
        }
    
    def export_metrics(self, format: str = 'json') -> str:
        """
        Export metrics in specified format.
        
        Args:
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported metrics string
        """
        if format == 'json':
            import json
            return json.dumps(self.get_metrics(), indent=2)
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Metric', 'Value'])
            
            # Write metrics
            metrics = self.get_metrics()
            for key, value in metrics.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        writer.writerow([f'{key}.{sub_key}', sub_value])
                else:
                    writer.writerow([key, value])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.success_count = 0
        self.error_count = 0
        self.response_times.clear()
        self.error_history.clear()
        self.memory_usage.clear()
        self.cpu_usage.clear()
        self.component_health.clear()
        self.start_time = time.time()
        
        self.logger.info("Metrics reset")
    
    def set_threshold(self, metric: str, value: float):
        """
        Set threshold for a metric.
        
        Args:
            metric: Metric name
            value: Threshold value
        """
        if metric in self.thresholds:
            self.thresholds[metric] = value
            self.logger.info(f"Threshold for {metric} set to {value}")
        else:
            self.logger.warning(f"Unknown metric: {metric}")
    
    def get_thresholds(self) -> Dict[str, float]:
        """
        Get current thresholds.
        
        Returns:
            Dictionary containing current thresholds
        """
        return self.thresholds.copy()