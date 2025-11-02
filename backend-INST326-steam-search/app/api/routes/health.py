"""
Steam Game Search Engine - Health API Routes
健康检查API路由模块

This module contains health check and system status endpoints for monitoring
and service availability verification.
该模块包含健康检查和系统状态端点，用于监控和服务可用性验证。
"""

from fastapi import APIRouter, Request, Depends
from typing import Dict, Any
import logging
import time

from ...core import get_search_engine, GameSearchEngine
from ..schemas.health import HealthResponse, SystemStatusResponse
from ...utils.logging import log_api_request, PerformanceTimer

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)

# 创建路由器 / Create router
router = APIRouter(tags=["health"])


def get_client_info(request: Request) -> Dict[str, str]:
    """
    获取客户端信息
    Get client information from request.
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        Dict[str, str]: 客户端信息
    """
    return {
        'client_ip': request.client.host if request.client else 'unknown',
        'user_agent': request.headers.get('user-agent', 'unknown')
    }


@router.get("/health", response_model=HealthResponse)
async def health_check(
    request: Request = None,
    search_engine: GameSearchEngine = Depends(get_search_engine)
) -> HealthResponse:
    """
    系统健康检查端点
    System health check endpoint for monitoring service availability.
    
    检查系统各组件的健康状态，包括搜索引擎、数据提供者、安全管理器等。
    Checks the health status of system components including search engine, data provider, security manager, etc.
    
    Args:
        request: FastAPI请求对象
        search_engine: 搜索引擎实例
        
    Returns:
        HealthResponse: 健康状态响应，包含总体状态和各组件详细信息
    """
    start_time = time.time()
    client_info = get_client_info(request)
    
    try:
        with PerformanceTimer("health_check_api", auto_log=False):
            # 获取搜索引擎健康状态 / Get search engine health status
            if search_engine and search_engine.initialized:
                health_status = search_engine.get_health_status()
            else:
                # 搜索引擎未初始化 / Search engine not initialized
                health_status = {
                    'status': 'unhealthy',
                    'timestamp': time.time(),
                    'components': {
                        'search_engine': {
                            'status': 'unhealthy',
                            'error': 'Search engine not initialized'
                        }
                    },
                    'version': '2.0.0'
                }
            
            # 构建健康响应 / Build health response
            # 处理时间戳格式 / Handle timestamp format
            timestamp_value = health_status.get('timestamp')
            if isinstance(timestamp_value, str):
                # 如果是ISO格式字符串，转换为Unix时间戳 / Convert ISO string to Unix timestamp
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(timestamp_value.replace('Z', '+00:00'))
                    timestamp_int = int(dt.timestamp())
                except ValueError:
                    timestamp_int = int(time.time())
            else:
                timestamp_int = int(time.time())

            response = HealthResponse(
                status=health_status['status'],
                timestamp=timestamp_int,
                services=_extract_service_status(health_status.get('components', {})),
                version=health_status.get('version', '2.0.0'),
                uptime=_calculate_uptime(health_status),
                performance_metrics=health_status.get('performance_metrics', {})
            )
            
            # 记录健康检查 / Log health check
            logger.info(f"Health check completed: status={response.status}")
            return response
            
    except Exception as e:
        # 健康检查失败 / Health check failed
        logger.error(f"Health check error: {str(e)}")
        return HealthResponse(
            status='unhealthy',
            timestamp=int(time.time()),
            services={'error': str(e)},
            version='2.0.0',
            uptime=0,
            performance_metrics={}
        )
    finally:
        # 记录API请求日志 / Log API request
        duration = time.time() - start_time
        log_api_request(
            method="GET",
            path="/api/v1/health",
            status_code=200,
            duration=duration,
            client_ip=client_info['client_ip'],
            user_agent=client_info['user_agent']
        )


@router.get("/status", response_model=SystemStatusResponse)
async def system_status(
    request: Request = None,
    search_engine: GameSearchEngine = Depends(get_search_engine)
) -> SystemStatusResponse:
    """
    系统详细状态端点
    Detailed system status endpoint with comprehensive information.
    
    提供系统的详细状态信息，包括性能指标、统计数据和配置信息。
    Provides detailed system status information including performance metrics, statistics, and configuration.
    
    Args:
        request: FastAPI请求对象
        search_engine: 搜索引擎实例
        
    Returns:
        SystemStatusResponse: 系统状态响应，包含详细的系统信息
    """
    start_time = time.time()
    client_info = get_client_info(request)
    
    try:
        with PerformanceTimer("system_status_api"):
            # 获取系统统计信息 / Get system statistics
            if search_engine and search_engine.initialized:
                statistics = search_engine.get_statistics()
                health_status = search_engine.get_health_status()
            else:
                statistics = {'status': 'not_initialized'}
                health_status = {'status': 'unhealthy'}
            
            # 构建系统状态响应 / Build system status response
            response = SystemStatusResponse(
                status=health_status.get('status', 'unknown'),
                timestamp=int(time.time()),
                version='2.0.0',
                environment='development',  # 可以从配置中获取
                uptime=_calculate_uptime(health_status),
                components=health_status.get('components', {}),
                statistics=statistics,
                configuration={
                    'search_enabled': True,
                    'mock_data_enabled': True,
                    'security_enabled': True,
                    'health_monitoring_enabled': True
                }
            )
            
            logger.info(f"System status retrieved: status={response.status}")
            return response
            
    except Exception as e:
        # 系统状态检查失败 / System status check failed
        logger.error(f"System status error: {str(e)}")
        return SystemStatusResponse(
            status='error',
            timestamp=int(time.time()),
            version='2.0.0',
            environment='unknown',
            uptime=0,
            components={'error': str(e)},
            statistics={'error': str(e)},
            configuration={}
        )
    finally:
        # 记录API请求日志 / Log API request
        duration = time.time() - start_time
        log_api_request(
            method="GET",
            path="/api/v1/status",
            status_code=200,
            duration=duration,
            client_ip=client_info['client_ip'],
            user_agent=client_info['user_agent']
        )


@router.get("/ping")
async def ping(request: Request = None) -> Dict[str, Any]:
    """
    简单的ping端点
    Simple ping endpoint for basic connectivity check.
    
    提供最基本的连通性检查，返回简单的pong响应。
    Provides basic connectivity check with simple pong response.
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        Dict[str, Any]: 简单的pong响应
    """
    start_time = time.time()
    client_info = get_client_info(request)
    
    try:
        response = {
            'message': 'pong',
            'timestamp': int(time.time()),
            'version': '2.0.0'
        }
        
        logger.debug("Ping request processed")
        return response
        
    finally:
        # 记录API请求日志 / Log API request
        duration = time.time() - start_time
        log_api_request(
            method="GET",
            path="/api/v1/ping",
            status_code=200,
            duration=duration,
            client_ip=client_info['client_ip'],
            user_agent=client_info['user_agent']
        )


def _extract_service_status(components: Dict[str, Any]) -> Dict[str, str]:
    """
    从组件信息中提取服务状态
    Extract service status from component information.
    
    Args:
        components: 组件信息字典
        
    Returns:
        Dict[str, str]: 服务状态字典
    """
    services = {}
    
    for component_name, component_info in components.items():
        if isinstance(component_info, dict):
            services[component_name] = component_info.get('status', 'unknown')
        else:
            services[component_name] = str(component_info)
    
    return services


def _calculate_uptime(health_status: Dict[str, Any]) -> int:
    """
    计算系统运行时间
    Calculate system uptime in seconds.
    
    Args:
        health_status: 健康状态信息
        
    Returns:
        int: 运行时间（秒）
    """
    try:
        performance_metrics = health_status.get('performance_metrics', {})
        uptime = performance_metrics.get('uptime_seconds', 0)
        return int(uptime)
    except Exception:
        return 0
