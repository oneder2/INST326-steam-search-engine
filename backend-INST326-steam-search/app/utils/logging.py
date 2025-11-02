"""
Steam Game Search Engine - Logging Utilities
日志工具模块

This module provides logging utilities and security event logging.
该模块提供日志工具和安全事件记录功能。
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

from ..config.constants import LOG_FORMAT, SECURITY_LOG_FORMAT


# 配置安全日志记录器 / Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# 配置性能日志记录器 / Configure performance logger
performance_logger = logging.getLogger('performance')
performance_logger.setLevel(logging.INFO)


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    设置应用程序日志配置
    Setup application logging configuration
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径（可选）
    """
    # 配置根日志记录器 / Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=LOG_FORMAT,
        handlers=[]
    )
    
    # 添加控制台处理器 / Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger().addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器 / Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logging.getLogger().addHandler(file_handler)
    
    # 配置安全日志记录器 / Configure security logger
    security_handler = logging.StreamHandler()
    security_handler.setFormatter(logging.Formatter(SECURITY_LOG_FORMAT))
    security_logger.addHandler(security_handler)
    
    if log_file:
        security_file_handler = logging.FileHandler(f"security_{log_file}")
        security_file_handler.setFormatter(logging.Formatter(SECURITY_LOG_FORMAT))
        security_logger.addHandler(security_file_handler)


def log_security_event(
    event_type: str,
    details: Dict[str, Any],
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    severity: str = "INFO"
) -> None:
    """
    记录安全事件到专用日志
    Log security events to dedicated security log
    
    Args:
        event_type: 事件类型（如 'malicious_input', 'rate_limit_exceeded'）
        details: 事件详细信息字典
        client_ip: 客户端IP地址
        user_agent: 用户代理字符串
        severity: 严重程度级别
    """
    event_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'severity': severity,
        'client_ip': client_ip,
        'user_agent': user_agent,
        'details': details
    }
    
    # 记录到安全日志 / Log to security logger
    log_message = f"Security Event: {event_type} | {json.dumps(event_data, ensure_ascii=False)}"
    
    if severity == "CRITICAL":
        security_logger.critical(log_message)
    elif severity == "ERROR":
        security_logger.error(log_message)
    elif severity == "WARNING":
        security_logger.warning(log_message)
    else:
        security_logger.info(log_message)


def log_performance_metric(
    operation: str,
    duration: float,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    记录性能指标
    Log performance metrics
    
    Args:
        operation: 操作名称
        duration: 执行时间（秒）
        details: 额外详细信息
    """
    metric_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'operation': operation,
        'duration_seconds': round(duration, 4),
        'details': details or {}
    }
    
    log_message = f"Performance: {operation} | Duration: {duration:.4f}s | {json.dumps(metric_data, ensure_ascii=False)}"
    performance_logger.info(log_message)


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    query_params: Optional[Dict[str, Any]] = None
) -> None:
    """
    记录API请求信息
    Log API request information
    
    Args:
        method: HTTP方法
        path: 请求路径
        status_code: 响应状态码
        duration: 请求处理时间
        client_ip: 客户端IP
        user_agent: 用户代理
        query_params: 查询参数
    """
    request_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'method': method,
        'path': path,
        'status_code': status_code,
        'duration_seconds': round(duration, 4),
        'client_ip': client_ip,
        'user_agent': user_agent,
        'query_params': query_params
    }
    
    logger = logging.getLogger('api')
    log_message = f"API Request: {method} {path} | Status: {status_code} | Duration: {duration:.4f}s"
    
    if status_code >= 500:
        logger.error(f"{log_message} | {json.dumps(request_data, ensure_ascii=False)}")
    elif status_code >= 400:
        logger.warning(f"{log_message} | {json.dumps(request_data, ensure_ascii=False)}")
    else:
        logger.info(f"{log_message} | {json.dumps(request_data, ensure_ascii=False)}")


def log_search_query(
    query: str,
    results_count: int,
    duration: float,
    filters: Optional[Dict[str, Any]] = None,
    client_ip: Optional[str] = None
) -> None:
    """
    记录搜索查询信息
    Log search query information
    
    Args:
        query: 搜索查询
        results_count: 结果数量
        duration: 搜索时间
        filters: 应用的过滤器
        client_ip: 客户端IP
    """
    search_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'query': query,
        'results_count': results_count,
        'duration_seconds': round(duration, 4),
        'filters': filters,
        'client_ip': client_ip
    }
    
    logger = logging.getLogger('search')
    log_message = f"Search Query: '{query}' | Results: {results_count} | Duration: {duration:.4f}s"
    logger.info(f"{log_message} | {json.dumps(search_data, ensure_ascii=False)}")


class PerformanceTimer:
    """
    性能计时器上下文管理器
    Performance timer context manager
    """
    
    def __init__(self, operation_name: str, auto_log: bool = True):
        """
        初始化性能计时器
        Initialize performance timer
        
        Args:
            operation_name: 操作名称
            auto_log: 是否自动记录日志
        """
        self.operation_name = operation_name
        self.auto_log = auto_log
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        """进入上下文管理器"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        self.end_time = time.time()
        if self.auto_log:
            duration = self.end_time - self.start_time
            log_performance_metric(self.operation_name, duration)
    
    @property
    def duration(self) -> Optional[float]:
        """获取执行时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
