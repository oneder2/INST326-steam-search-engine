"""
Steam Game Search Engine - Health Monitor
健康监控类，监控系统各组件状态

This module provides health monitoring functionality for system components
including data provider, search service, and security manager.
"""

import time
import psutil
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ...config.settings import Settings
from ...config.constants import HealthStatus

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    健康监控类，监控系统各组件状态
    Health monitor class for system component status monitoring.
    
    这个类监控各个系统组件的健康状态，提供统一的健康检查接口。
    This class monitors the health status of system components and provides unified health check interface.
    """
    
    def __init__(self, config: Settings):
        """
        初始化健康监控器
        Initialize health monitor with component tracking.
        
        Args:
            config (Settings): 应用程序配置
        """
        self.config = config
        self.last_check_time: Optional[float] = None
        self.cached_status: Optional[Dict[str, Any]] = None
        self.cache_duration = 30  # 缓存30秒 / Cache for 30 seconds
        
        # 组件状态跟踪 / Component status tracking
        self.component_status = {
            'api': HealthStatus.UNKNOWN.value,
            'data_repository': HealthStatus.UNKNOWN.value,
            'search_service': HealthStatus.UNKNOWN.value,
            'security_manager': HealthStatus.UNKNOWN.value,
            'system_resources': HealthStatus.UNKNOWN.value
        }
        
        # 性能指标 / Performance metrics
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'uptime_seconds': 0,
            'start_time': time.time()
        }
        
        # 系统资源阈值 / System resource thresholds
        self.cpu_threshold = 80.0  # CPU使用率阈值
        self.memory_threshold = 80.0  # 内存使用率阈值
        self.disk_threshold = 90.0  # 磁盘使用率阈值
        
        logger.info("HealthMonitor initialized")
    
    def get_comprehensive_health_status(self) -> Dict[str, Any]:
        """
        获取全面的健康状态信息
        Get comprehensive health status information.
        
        Returns:
            Dict[str, Any]: 健康状态信息
        """
        current_time = time.time()
        
        # 检查缓存是否有效 / Check if cache is valid
        if (self.cached_status and self.last_check_time and 
            current_time - self.last_check_time < self.cache_duration):
            return self.cached_status
        
        # 执行健康检查 / Perform health check
        health_status = self._perform_health_check()
        
        # 更新缓存 / Update cache
        self.cached_status = health_status
        self.last_check_time = current_time
        
        return health_status
    
    def _perform_health_check(self) -> Dict[str, Any]:
        """
        执行实际的健康检查
        Perform actual health check on all components.
        
        Returns:
            Dict[str, Any]: 健康检查结果
        """
        try:
            # 检查系统资源 / Check system resources
            system_health = self._check_system_resources()
            
            # 检查各个组件 / Check components
            api_health = self._check_api_health()
            data_health = self._check_data_repository_health()
            search_health = self._check_search_service_health()
            security_health = self._check_security_manager_health()
            
            # 更新组件状态 / Update component status
            self.component_status.update({
                'api': api_health['status'],
                'data_repository': data_health['status'],
                'search_service': search_health['status'],
                'security_manager': security_health['status'],
                'system_resources': system_health['status']
            })
            
            # 计算总体健康状态 / Calculate overall health status
            overall_status = self._calculate_overall_status()
            
            # 更新性能指标 / Update performance metrics
            self._update_performance_metrics()
            
            return {
                'status': overall_status,
                'timestamp': datetime.utcnow().isoformat(),
                'components': {
                    'api': api_health,
                    'data_repository': data_health,
                    'search_service': search_health,
                    'security_manager': security_health,
                    'system_resources': system_health
                },
                'performance_metrics': self.performance_metrics.copy(),
                'version': self.config.api_version
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'version': self.config.api_version
            }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源状态 / Check system resource status"""
        try:
            # CPU使用率 / CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率 / Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率 / Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # 确定状态 / Determine status
            if (cpu_percent > self.cpu_threshold or 
                memory_percent > self.memory_threshold or 
                disk_percent > self.disk_threshold):
                status = HealthStatus.DEGRADED.value
            else:
                status = HealthStatus.HEALTHY.value
            
            return {
                'status': status,
                'cpu_percent': round(cpu_percent, 2),
                'memory_percent': round(memory_percent, 2),
                'disk_percent': round(disk_percent, 2),
                'details': {
                    'cpu_threshold': self.cpu_threshold,
                    'memory_threshold': self.memory_threshold,
                    'disk_threshold': self.disk_threshold
                }
            }
            
        except Exception as e:
            logger.error(f"System resource check failed: {str(e)}")
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'error': str(e)
            }
    
    def _check_api_health(self) -> Dict[str, Any]:
        """检查API健康状态 / Check API health status"""
        try:
            # 简单的API健康检查 / Simple API health check
            return {
                'status': HealthStatus.HEALTHY.value,
                'details': {
                    'total_requests': self.performance_metrics['total_requests'],
                    'success_rate': self._calculate_success_rate()
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'error': str(e)
            }
    
    def _check_data_repository_health(self) -> Dict[str, Any]:
        """检查数据仓库健康状态 / Check data repository health status"""
        try:
            # 模拟数据仓库健康检查 / Mock data repository health check
            return {
                'status': HealthStatus.HEALTHY.value,
                'details': {
                    'provider_type': 'mock',
                    'data_available': True
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'error': str(e)
            }
    
    def _check_search_service_health(self) -> Dict[str, Any]:
        """检查搜索服务健康状态 / Check search service health status"""
        try:
            # 模拟搜索服务健康检查 / Mock search service health check
            return {
                'status': HealthStatus.HEALTHY.value,
                'details': {
                    'bm25_enabled': True,
                    'semantic_enabled': True,
                    'fusion_enabled': True
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'error': str(e)
            }
    
    def _check_security_manager_health(self) -> Dict[str, Any]:
        """检查安全管理器健康状态 / Check security manager health status"""
        try:
            # 模拟安全管理器健康检查 / Mock security manager health check
            return {
                'status': HealthStatus.HEALTHY.value,
                'details': {
                    'rate_limiting_enabled': True,
                    'malicious_pattern_detection_enabled': True
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'error': str(e)
            }
    
    def _calculate_overall_status(self) -> str:
        """计算总体健康状态 / Calculate overall health status"""
        statuses = list(self.component_status.values())
        
        # 如果有任何组件不健康，总体状态为不健康 / If any component is unhealthy, overall is unhealthy
        if HealthStatus.UNHEALTHY.value in statuses:
            return HealthStatus.UNHEALTHY.value
        
        # 如果有任何组件降级，总体状态为降级 / If any component is degraded, overall is degraded
        if HealthStatus.DEGRADED.value in statuses:
            return HealthStatus.DEGRADED.value
        
        # 如果所有组件都健康，总体状态为健康 / If all components are healthy, overall is healthy
        if all(status == HealthStatus.HEALTHY.value for status in statuses):
            return HealthStatus.HEALTHY.value
        
        # 默认为未知状态 / Default to unknown status
        return HealthStatus.UNKNOWN.value
    
    def _update_performance_metrics(self):
        """更新性能指标 / Update performance metrics"""
        current_time = time.time()
        self.performance_metrics['uptime_seconds'] = int(current_time - self.performance_metrics['start_time'])
    
    def _calculate_success_rate(self) -> float:
        """计算成功率 / Calculate success rate"""
        total = self.performance_metrics['total_requests']
        if total == 0:
            return 100.0
        
        successful = self.performance_metrics['successful_requests']
        return round((successful / total) * 100, 2)
    
    def record_request(self, success: bool, response_time: float):
        """
        记录请求信息
        Record request information for metrics.
        
        Args:
            success (bool): 请求是否成功
            response_time (float): 响应时间（秒）
        """
        self.performance_metrics['total_requests'] += 1
        
        if success:
            self.performance_metrics['successful_requests'] += 1
        else:
            self.performance_metrics['failed_requests'] += 1
        
        # 更新平均响应时间 / Update average response time
        total_requests = self.performance_metrics['total_requests']
        current_avg = self.performance_metrics['average_response_time']
        new_avg = ((current_avg * (total_requests - 1)) + response_time) / total_requests
        self.performance_metrics['average_response_time'] = round(new_avg, 4)
    
    def get_quick_status(self) -> str:
        """
        获取快速状态检查
        Get quick status check without detailed information.
        
        Returns:
            str: 健康状态字符串
        """
        try:
            # 简单的系统资源检查 / Simple system resource check
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 90 or memory_percent > 90:
                return HealthStatus.UNHEALTHY.value
            elif cpu_percent > 70 or memory_percent > 70:
                return HealthStatus.DEGRADED.value
            else:
                return HealthStatus.HEALTHY.value
                
        except Exception:
            return HealthStatus.UNKNOWN.value
    
    def stop_monitoring(self):
        """停止监控 / Stop monitoring"""
        logger.info("HealthMonitor stopped")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取健康监控统计信息
        Get health monitoring statistics.
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            'component_status': self.component_status.copy(),
            'performance_metrics': self.performance_metrics.copy(),
            'cache_info': {
                'last_check_time': self.last_check_time,
                'cache_duration': self.cache_duration,
                'cached_status_available': self.cached_status is not None
            }
        }
