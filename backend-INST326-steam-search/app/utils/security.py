"""
Steam Game Search Engine - Security Utilities
安全工具模块

This module provides security-related utilities including input sanitization
and malicious pattern detection.
该模块提供安全相关工具，包括输入清理和恶意模式检测。
"""

import re
import hashlib
from typing import Dict, List, Any, Optional
from urllib.parse import unquote

from ..config.constants import MALICIOUS_PATTERNS


def sanitize_input(input_text: str, max_length: int = 1000) -> str:
    """
    清理用户输入以确保安全性和数据完整性
    Sanitize user input for security and data integrity
    
    Args:
        input_text: 要清理的原始用户输入文本
        max_length: 允许的最大长度
        
    Returns:
        str: 清理后的安全输入文本
    """
    if not input_text:
        return ""
    
    # 移除空字节和控制字符 / Remove null bytes and control characters
    sanitized = input_text.replace('\x00', '').replace('\r', '')
    
    # 标准化空白字符 / Normalize whitespace
    sanitized = ' '.join(sanitized.split())
    
    # 移除潜在有害模式 / Remove potentially harmful patterns
    harmful_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
    for pattern in harmful_patterns:
        sanitized = sanitized.replace(pattern.lower(), '')
        sanitized = sanitized.replace(pattern.upper(), '')
    
    # 截断到最大长度 / Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].strip()
    
    return sanitized.strip()


def detect_malicious_patterns(input_text: str, strict_mode: bool = False) -> Dict[str, Any]:
    """
    检测用户输入中的潜在恶意模式
    Detect potentially malicious patterns in user input
    
    Args:
        input_text: 要分析的用户输入文本
        strict_mode: 是否启用更严格的检测规则
        
    Returns:
        Dict[str, Any]: 包含威胁级别和详细信息的检测结果
    """
    if not input_text:
        return {
            'is_malicious': False,
            'threat_level': 'none',
            'detected_patterns': [],
            'risk_score': 0.0
        }
    
    # 解码URL编码以捕获混淆攻击 / Decode URL encoding to catch obfuscated attacks
    decoded_text = unquote(input_text).lower()
    
    detected_threats = []
    risk_score = 0.0
    
    # 检查不同类型的攻击 / Check for different types of attacks
    sql_threats = _detect_sql_injection(decoded_text, strict_mode)
    xss_threats = _detect_xss_patterns(decoded_text, strict_mode)
    cmd_threats = _detect_command_injection(decoded_text, strict_mode)
    
    # 合并所有威胁 / Combine all threats
    all_threats = sql_threats + xss_threats + cmd_threats
    
    # 计算总体风险分数 / Calculate overall risk score
    for threat in all_threats:
        risk_score += threat['severity']
        detected_threats.append(threat)
    
    # 确定威胁级别 / Determine threat level
    threat_level = _calculate_threat_level(risk_score)
    
    return {
        'is_malicious': len(detected_threats) > 0,
        'threat_level': threat_level,
        'detected_patterns': detected_threats,
        'risk_score': min(risk_score, 10.0),  # 上限为10.0 / Cap at 10.0
        'input_length': len(input_text),
        'analysis_mode': 'strict' if strict_mode else 'normal'
    }


def generate_request_id() -> str:
    """
    生成唯一的请求ID
    Generate unique request ID for tracking
    
    Returns:
        str: 唯一请求ID
    """
    import time
    import random
    
    timestamp = str(int(time.time() * 1000))
    random_part = str(random.randint(1000, 9999))
    request_id = f"{timestamp}-{random_part}"
    
    return hashlib.md5(request_id.encode()).hexdigest()[:12]


def validate_search_query(query: str) -> Dict[str, Any]:
    """
    验证搜索查询的安全性和有效性
    Validate search query for security and validity
    
    Args:
        query: 搜索查询字符串
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    if not query:
        return {
            'is_valid': False,
            'error': 'Empty query',
            'sanitized_query': ''
        }
    
    # 检查长度 / Check length
    if len(query) > 500:
        return {
            'is_valid': False,
            'error': 'Query too long',
            'sanitized_query': query[:500]
        }
    
    # 检查恶意模式 / Check for malicious patterns
    malicious_check = detect_malicious_patterns(query)
    if malicious_check['is_malicious']:
        return {
            'is_valid': False,
            'error': 'Potentially malicious query',
            'threat_info': malicious_check,
            'sanitized_query': sanitize_input(query)
        }
    
    # 清理查询 / Sanitize query
    sanitized = sanitize_input(query)
    
    return {
        'is_valid': True,
        'sanitized_query': sanitized,
        'original_length': len(query),
        'sanitized_length': len(sanitized)
    }


def _detect_sql_injection(text: str, strict_mode: bool) -> List[Dict[str, Any]]:
    """检测SQL注入模式 / Detect SQL injection patterns"""
    threats = []
    
    for pattern in MALICIOUS_PATTERNS['sql_injection']:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            threats.append({
                'type': 'sql_injection',
                'pattern': 'SQL Injection Pattern',
                'severity': 4.0,
                'matches': len(matches),
                'sample': str(matches[0])[:50]
            })
    
    return threats


def _detect_xss_patterns(text: str, strict_mode: bool) -> List[Dict[str, Any]]:
    """检测跨站脚本（XSS）模式 / Detect Cross-Site Scripting (XSS) patterns"""
    threats = []
    
    for pattern in MALICIOUS_PATTERNS['xss']:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            threats.append({
                'type': 'xss',
                'pattern': 'XSS Pattern',
                'severity': 4.0,
                'matches': len(matches),
                'sample': str(matches[0])[:50]
            })
    
    return threats


def _detect_command_injection(text: str, strict_mode: bool) -> List[Dict[str, Any]]:
    """检测命令注入模式 / Detect command injection patterns"""
    threats = []
    
    for pattern in MALICIOUS_PATTERNS['command_injection']:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            threats.append({
                'type': 'command_injection',
                'pattern': 'Command Injection Pattern',
                'severity': 5.0,
                'matches': len(matches),
                'sample': str(matches[0])[:50]
            })
    
    return threats


def _calculate_threat_level(risk_score: float) -> str:
    """计算威胁级别 / Calculate threat level"""
    if risk_score == 0:
        return 'none'
    elif risk_score < 3.0:
        return 'low'
    elif risk_score < 6.0:
        return 'medium'
    elif risk_score < 9.0:
        return 'high'
    else:
        return 'critical'
