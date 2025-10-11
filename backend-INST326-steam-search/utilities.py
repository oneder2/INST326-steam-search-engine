"""
工具函数模块
Utilities module for common functions and security features

这个模块包含了应用程序中使用的各种工具函数，包括：
- 输入清理和安全处理
- 文本处理和标准化
- 安全事件日志记录
- 恶意模式检测

This module contains various utility functions used throughout the application:
- Input sanitization and security processing
- Text processing and normalization  
- Security event logging
- Malicious pattern detection
"""

import re
import json
import time
import hashlib
import logging
import unicodedata
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import unquote

# 配置安全日志记录器 / Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

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


def normalize_text(text: str, lowercase: bool = True, remove_accents: bool = False) -> str:
    """
    标准化文本以确保一致的处理
    Normalize text for consistent processing and comparison
    
    Args:
        text: 要标准化的文本
        lowercase: 是否转换为小写
        remove_accents: 是否移除重音符号
        
    Returns:
        str: 标准化的文本字符串
    """
    if not text:
        return ""
    
    # Unicode标准化（NFC形式）/ Unicode normalization (NFC form)
    normalized = unicodedata.normalize('NFC', text)
    
    # 如果需要，转换为小写 / Convert to lowercase if requested
    if lowercase:
        normalized = normalized.lower()
    
    # 如果需要，移除重音符号 / Remove accent marks if requested
    if remove_accents:
        normalized = _remove_accent_marks(normalized)
    
    # 标准化空白字符 / Normalize whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # 移除前导/尾随空白字符 / Remove leading/trailing whitespace
    normalized = normalized.strip()
    
    return normalized


def _remove_accent_marks(text: str) -> str:
    """移除文本中的重音符号同时保留基本字符 / Remove accent marks from text while preserving base characters"""
    # 分解字符并移除组合标记 / Decompose characters and remove combining marks
    decomposed = unicodedata.normalize('NFD', text)
    without_accents = ''.join(
        char for char in decomposed 
        if unicodedata.category(char) != 'Mn'
    )
    return without_accents


def tokenize_text(text: str, language: str = "english", remove_stopwords: bool = True) -> List[str]:
    """
    为搜索索引和处理对文本进行分词
    Tokenize text for search indexing and processing
    
    Args:
        text: 要分词的文本
        language: 停用词和词干提取的语言
        remove_stopwords: 是否移除停用词
        
    Returns:
        List[str]: 标准化的词元列表
    """
    if not text:
        return []
    
    # 转换为小写 / Convert to lowercase
    text = text.lower()
    
    # 移除标点符号和特殊字符 / Remove punctuation and special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 分割为词元 / Split into tokens
    tokens = text.split()
    
    # 如果需要，移除停用词 / Remove stop words if requested
    if remove_stopwords:
        stop_words = _get_stop_words(language)
        tokens = [token for token in tokens if token not in stop_words]
    
    # 过滤掉很短的词元 / Filter out very short tokens
    tokens = [token for token in tokens if len(token) > 2]
    
    # 应用词干提取以获得更好的匹配 / Apply stemming for better matching
    stemmed_tokens = [_stem_word(token, language) for token in tokens]
    
    return stemmed_tokens


def _get_stop_words(language: str) -> set:
    """获取指定语言的停用词 / Get stop words for the specified language"""
    english_stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
    }
    
    if language == "english":
        return english_stop_words
    else:
        return set()  # 根据需要添加其他语言 / Add other languages as needed


def _stem_word(word: str, language: str) -> str:
    """常见后缀的简单词干提取 / Simple stemming for common suffixes"""
    if language == "english":
        # 移除常见后缀 / Remove common suffixes
        suffixes = ['ing', 'ed', 'er', 'est', 'ly', 's']
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
    return word


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


def _detect_sql_injection(text: str, strict_mode: bool) -> List[Dict[str, Any]]:
    """检测SQL注入模式 / Detect SQL injection patterns"""
    threats = []
    
    # 常见SQL注入模式 / Common SQL injection patterns
    sql_patterns = [
        (r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)", 3.0, "SQL Keywords"),
        (r"(--|#|/\*|\*/)", 2.0, "SQL Comments"),
        (r"(\bor\b.*=.*\bor\b|\band\b.*=.*\band\b)", 4.0, "SQL Boolean Logic"),
        (r"(';|';\s*--|';\s*#)", 5.0, "SQL Statement Termination"),
    ]
    
    for pattern, severity, description in sql_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            threats.append({
                'type': 'sql_injection',
                'pattern': description,
                'severity': severity,
                'matches': len(matches),
                'sample': matches[0] if isinstance(matches[0], str) else matches[0][0]
            })
    
    return threats


def _detect_xss_patterns(text: str, strict_mode: bool) -> List[Dict[str, Any]]:
    """检测跨站脚本（XSS）模式 / Detect Cross-Site Scripting (XSS) patterns"""
    threats = []
    
    xss_patterns = [
        (r"<script[^>]*>.*?</script>", 5.0, "Script Tags"),
        (r"javascript:", 4.0, "JavaScript Protocol"),
        (r"on\w+\s*=", 3.0, "Event Handlers"),
        (r"<iframe[^>]*>", 4.0, "Iframe Tags"),
    ]
    
    for pattern, severity, description in xss_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            threats.append({
                'type': 'xss',
                'pattern': description,
                'severity': severity,
                'matches': len(matches),
                'sample': matches[0][:50] + '...' if len(matches[0]) > 50 else matches[0]
            })
    
    return threats


def _detect_command_injection(text: str, strict_mode: bool) -> List[Dict[str, Any]]:
    """检测命令注入模式 / Detect command injection patterns"""
    threats = []
    
    cmd_patterns = [
        (r"(\||&|;|\$\(|\`)", 3.0, "Command Separators"),
        (r"\b(cat|ls|dir|type|copy|del|rm|mv|cp)\b", 2.0, "System Commands"),
    ]
    
    for pattern, severity, description in cmd_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            threats.append({
                'type': 'command_injection',
                'pattern': description,
                'severity': severity,
                'matches': len(matches),
                'sample': matches[0] if isinstance(matches[0], str) else matches[0][0]
            })
    
    return threats


def _calculate_threat_level(risk_score: float) -> str:
    """基于风险分数计算总体威胁级别 / Calculate overall threat level based on risk score"""
    if risk_score >= 8.0:
        return 'critical'
    elif risk_score >= 5.0:
        return 'high'
    elif risk_score >= 2.0:
        return 'medium'
    elif risk_score > 0.0:
        return 'low'
    else:
        return 'none'


def log_security_event(
    event_type: str, 
    details: Dict[str, Any], 
    severity: str = "info", 
    user_ip: Optional[str] = None
) -> bool:
    """
    记录安全相关事件
    Log security-related events with structured formatting
    
    Args:
        event_type: 安全事件类型
        details: 事件详细信息和上下文信息
        severity: 事件严重级别
        user_ip: 用户IP地址（如果可用）
        
    Returns:
        bool: 如果日志记录成功则返回True，否则返回False
    """
    try:
        # 生成唯一事件ID / Generate unique event ID
        event_id = _generate_event_id(event_type, details, user_ip)
        
        # 准备结构化日志条目 / Prepare structured log entry
        log_entry = {
            'event_id': event_id,
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': severity.upper(),
            'user_ip': user_ip or 'unknown',
            'details': _sanitize_log_details(details)
        }
        
        # 转换为JSON字符串进行结构化日志记录 / Convert to JSON string for structured logging
        log_message = json.dumps(log_entry, ensure_ascii=False, separators=(',', ':'))
        
        # 在适当级别记录日志 / Log at appropriate level
        log_level = getattr(logging, severity.upper(), logging.INFO)
        security_logger.log(log_level, log_message)
        
        return True
        
    except Exception as e:
        # 后备日志记录以防止日志失败破坏应用程序 / Fallback logging to prevent log failures
        security_logger.error(f"Failed to log security event: {str(e)}")
        return False


def _generate_event_id(event_type: str, details: Dict[str, Any], user_ip: Optional[str]) -> str:
    """生成用于跟踪的唯一事件ID / Generate unique event ID for tracking"""
    content = f"{event_type}:{user_ip}:{time.time()}:{json.dumps(details, sort_keys=True)}"
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]


def _sanitize_log_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """从日志详细信息中清理敏感信息 / Sanitize sensitive information from log details"""
    sanitized = {}
    
    # 要屏蔽的敏感键列表 / List of sensitive keys to mask
    sensitive_keys = {
        'password', 'token', 'api_key', 'secret', 'auth', 'session',
        'credit_card', 'ssn', 'email', 'phone'
    }
    
    for key, value in details.items():
        key_lower = key.lower()
        
        # 检查键是否包含敏感信息 / Check if key contains sensitive information
        is_sensitive = any(sensitive_word in key_lower for sensitive_word in sensitive_keys)
        
        if is_sensitive:
            # 屏蔽敏感值 / Mask sensitive values
            if isinstance(value, str) and len(value) > 4:
                sanitized[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
            else:
                sanitized[key] = '***MASKED***'
        else:
            # 保留非敏感值，但如果太长则截断 / Keep non-sensitive values, but truncate if too long
            if isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + '...[TRUNCATED]'
            else:
                sanitized[key] = value
    
    return sanitized
