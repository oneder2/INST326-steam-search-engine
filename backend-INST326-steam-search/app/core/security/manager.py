"""
Steam Game Search Engine - Security Manager
安全管理类，处理输入验证和安全检查

This module provides security functionality including input validation,
malicious pattern detection, and security event logging.
"""

import re
import time
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import unquote

from ...config.settings import Settings
from ...config.constants import MALICIOUS_PATTERNS, ERROR_MESSAGES
from ...utils.security import sanitize_input, detect_malicious_patterns, validate_search_query
from ...utils.logging import log_security_event

# 配置安全日志记录器 / Configure security logger
security_logger = logging.getLogger('security')
logger = logging.getLogger(__name__)


class SecurityManager:
    """
    安全管理类，处理输入验证和安全检查
    Security manager class for input validation and security checks.
    
    这个类整合了现有的安全功能，提供统一的安全管理接口。
    This class integrates existing security features and provides a unified security management interface.
    """
    
    def __init__(self, config: Settings):
        """
        初始化安全管理器
        Initialize security manager with security patterns and configurations.
        
        Args:
            config (Settings): 应用程序配置
        """
        self.config = config
        self.rate_limit_cache = {}  # 简单的速率限制缓存 / Simple rate limiting cache
        self.max_requests_per_minute = config.rate_limit_requests
        self.max_query_length = 500
        self.blocked_ips = set()
        
        # 安全统计 / Security statistics
        self.security_events_count = 0
        self.blocked_requests_count = 0
        self.validated_queries_count = 0
        
        logger.info("SecurityManager initialized with security patterns")
    
    def validate_search_query(self, query: str, client_ip: Optional[str] = None) -> Dict[str, Any]:
        """
        验证搜索查询的安全性和有效性
        Validate search query for security and validity.
        
        Args:
            query (str): 搜索查询字符串
            client_ip (Optional[str]): 客户端IP地址
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            self.validated_queries_count += 1
            
            # 使用工具函数进行验证 / Use utility function for validation
            validation_result = validate_search_query(query)
            
            # 如果查询无效，记录安全事件 / If query is invalid, log security event
            if not validation_result['is_valid']:
                self._log_security_event(
                    'invalid_query',
                    {
                        'query': query[:100],  # 限制日志中的查询长度
                        'error': validation_result['error'],
                        'threat_info': validation_result.get('threat_info', {})
                    },
                    client_ip,
                    severity='WARNING'
                )
                self.security_events_count += 1
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating search query: {str(e)}")
            return {
                'is_valid': False,
                'error': 'Validation error',
                'sanitized_query': sanitize_input(query) if query else ''
            }
    
    def validate_game_id(self, game_id: Any) -> bool:
        """
        验证游戏ID的有效性
        Validate game ID for validity.
        
        Args:
            game_id: 游戏ID（任意类型）
            
        Returns:
            bool: 是否有效
        """
        try:
            # 转换为整数 / Convert to integer
            id_val = int(game_id)
            
            # 检查范围 / Check range
            if id_val <= 0 or id_val > 999999999:  # 合理的Steam游戏ID范围
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False
    
    def check_rate_limit(self, client_ip: str, endpoint: str = "default") -> bool:
        """
        检查客户端是否超过速率限制
        Check if client exceeds rate limit.
        
        Args:
            client_ip (str): 客户端IP地址
            endpoint (str): 端点名称
            
        Returns:
            bool: 是否允许请求（True表示允许，False表示超限）
        """
        if client_ip in self.blocked_ips:
            self.blocked_requests_count += 1
            return False
        
        current_time = time.time()
        cache_key = f"{client_ip}:{endpoint}"
        
        # 获取或创建速率限制记录 / Get or create rate limit record
        if cache_key not in self.rate_limit_cache:
            self.rate_limit_cache[cache_key] = {
                'requests': [],
                'blocked_until': 0
            }
        
        rate_data = self.rate_limit_cache[cache_key]
        
        # 检查是否仍在阻止期内 / Check if still in blocking period
        if current_time < rate_data['blocked_until']:
            self.blocked_requests_count += 1
            return False
        
        # 清理过期的请求记录 / Clean expired request records
        minute_ago = current_time - 60
        rate_data['requests'] = [req_time for req_time in rate_data['requests'] if req_time > minute_ago]
        
        # 检查是否超过限制 / Check if exceeds limit
        if len(rate_data['requests']) >= self.max_requests_per_minute:
            # 阻止该IP 5分钟 / Block IP for 5 minutes
            rate_data['blocked_until'] = current_time + 300
            
            self._log_security_event(
                'rate_limit_exceeded',
                {
                    'endpoint': endpoint,
                    'requests_count': len(rate_data['requests']),
                    'limit': self.max_requests_per_minute
                },
                client_ip,
                severity='WARNING'
            )
            
            self.blocked_requests_count += 1
            return False
        
        # 记录当前请求 / Record current request
        rate_data['requests'].append(current_time)
        return True
    
    def sanitize_input(self, input_text: str, max_length: int = 1000) -> str:
        """
        清理用户输入
        Sanitize user input for security.
        
        Args:
            input_text (str): 原始输入文本
            max_length (int): 最大长度
            
        Returns:
            str: 清理后的文本
        """
        return sanitize_input(input_text, max_length)
    
    def detect_malicious_patterns(self, input_text: str, strict_mode: bool = False) -> Dict[str, Any]:
        """
        检测恶意模式
        Detect malicious patterns in input.
        
        Args:
            input_text (str): 输入文本
            strict_mode (bool): 是否启用严格模式
            
        Returns:
            Dict[str, Any]: 检测结果
        """
        return detect_malicious_patterns(input_text, strict_mode)
    
    def generate_request_id(self) -> str:
        """
        生成唯一的请求ID
        Generate unique request ID for tracking.
        
        Returns:
            str: 唯一请求ID
        """
        timestamp = str(int(time.time() * 1000))
        random_part = str(hash(timestamp) % 10000)
        request_id = f"{timestamp}-{random_part}"
        
        return hashlib.md5(request_id.encode()).hexdigest()[:12]
    
    def block_ip(self, ip_address: str, reason: str = "Security violation"):
        """
        阻止IP地址
        Block IP address for security reasons.
        
        Args:
            ip_address (str): 要阻止的IP地址
            reason (str): 阻止原因
        """
        self.blocked_ips.add(ip_address)
        
        self._log_security_event(
            'ip_blocked',
            {
                'reason': reason,
                'blocked_ips_count': len(self.blocked_ips)
            },
            ip_address,
            severity='ERROR'
        )
        
        logger.warning(f"IP {ip_address} blocked: {reason}")
    
    def unblock_ip(self, ip_address: str):
        """
        解除IP地址阻止
        Unblock IP address.
        
        Args:
            ip_address (str): 要解除阻止的IP地址
        """
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            logger.info(f"IP {ip_address} unblocked")
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """
        检查IP是否被阻止
        Check if IP address is blocked.
        
        Args:
            ip_address (str): IP地址
            
        Returns:
            bool: 是否被阻止
        """
        return ip_address in self.blocked_ips
    
    def _log_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        severity: str = "INFO"
    ):
        """
        记录安全事件
        Log security event with details.
        
        Args:
            event_type (str): 事件类型
            details (Dict[str, Any]): 事件详细信息
            client_ip (Optional[str]): 客户端IP
            user_agent (Optional[str]): 用户代理
            severity (str): 严重程度
        """
        log_security_event(event_type, details, client_ip, user_agent, severity)
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        获取安全状态信息
        Get security status information.
        
        Returns:
            Dict[str, Any]: 安全状态信息
        """
        return {
            'blocked_ips_count': len(self.blocked_ips),
            'rate_limit_entries': len(self.rate_limit_cache),
            'security_events_count': self.security_events_count,
            'blocked_requests_count': self.blocked_requests_count,
            'validated_queries_count': self.validated_queries_count,
            'max_requests_per_minute': self.max_requests_per_minute,
            'max_query_length': self.max_query_length
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取安全管理器统计信息
        Get security manager statistics.
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return self.get_security_status()
    
    def cleanup_expired_cache(self):
        """
        清理过期的缓存条目
        Clean up expired cache entries.
        """
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.rate_limit_cache.items():
            # 清理过期的请求记录 / Clean expired request records
            minute_ago = current_time - 60
            data['requests'] = [req_time for req_time in data['requests'] if req_time > minute_ago]
            
            # 如果没有最近的请求且不在阻止期内，标记为过期 / Mark as expired if no recent requests and not blocked
            if not data['requests'] and current_time >= data['blocked_until']:
                expired_keys.append(key)
        
        # 删除过期的缓存条目 / Remove expired cache entries
        for key in expired_keys:
            del self.rate_limit_cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired rate limit cache entries")
