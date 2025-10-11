# log_security_event

## log_security_event

**Category:** Utilities
**Complexity:** Low
**Last Updated:** 2024-10-11

### Description
Logs security-related events with structured formatting for monitoring and analysis. Provides comprehensive logging of security incidents, user activities, and system events with proper categorization and alerting capabilities.

### Signature
```python
def log_security_event(event_type: str, details: Dict[str, Any], severity: str = "info", user_ip: Optional[str] = None) -> bool:
```

### Parameters
- `event_type` (str, required): Type of security event (e.g., "malicious_input", "failed_auth", "suspicious_activity")
- `details` (Dict[str, Any], required): Event details and context information
- `severity` (str, optional): Event severity level ("debug", "info", "warning", "error", "critical") (default: "info")
- `user_ip` (Optional[str], optional): User IP address if available (default: None)

### Returns
- `bool`: True if logging was successful, False otherwise

### Example
```python
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Create file handler for security logs
security_handler = logging.FileHandler('logs/security.log')
security_handler.setLevel(logging.INFO)

# Create formatter for structured logging
security_formatter = logging.Formatter(
    '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
)
security_handler.setFormatter(security_formatter)
security_logger.addHandler(security_handler)

def log_security_event(
    event_type: str, 
    details: Dict[str, Any], 
    severity: str = "info", 
    user_ip: Optional[str] = None
) -> bool:
    """
    Log security events with structured formatting
    """
    try:
        # Generate unique event ID
        event_id = generate_event_id(event_type, details, user_ip)
        
        # Prepare structured log entry
        log_entry = {
            'event_id': event_id,
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': severity.upper(),
            'user_ip': user_ip or 'unknown',
            'details': sanitize_log_details(details),
            'system_info': get_system_context()
        }
        
        # Convert to JSON string for structured logging
        log_message = json.dumps(log_entry, ensure_ascii=False, separators=(',', ':'))
        
        # Log at appropriate level
        log_level = getattr(logging, severity.upper(), logging.INFO)
        security_logger.log(log_level, log_message)
        
        # Send alerts for high-severity events
        if severity.lower() in ['error', 'critical']:
            send_security_alert(log_entry)
        
        return True
        
    except Exception as e:
        # Fallback logging to prevent log failures from breaking the application
        security_logger.error(f"Failed to log security event: {str(e)}")
        return False

def generate_event_id(event_type: str, details: Dict[str, Any], user_ip: Optional[str]) -> str:
    """Generate unique event ID for tracking"""
    # Create a hash based on event details and timestamp
    content = f"{event_type}:{user_ip}:{time.time()}:{json.dumps(details, sort_keys=True)}"
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

def sanitize_log_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize sensitive information from log details"""
    sanitized = {}
    
    # List of sensitive keys to mask
    sensitive_keys = {
        'password', 'token', 'api_key', 'secret', 'auth', 'session',
        'credit_card', 'ssn', 'email', 'phone'
    }
    
    for key, value in details.items():
        key_lower = key.lower()
        
        # Check if key contains sensitive information
        is_sensitive = any(sensitive_word in key_lower for sensitive_word in sensitive_keys)
        
        if is_sensitive:
            # Mask sensitive values
            if isinstance(value, str) and len(value) > 4:
                sanitized[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
            else:
                sanitized[key] = '***MASKED***'
        else:
            # Keep non-sensitive values, but truncate if too long
            if isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + '...[TRUNCATED]'
            else:
                sanitized[key] = value
    
    return sanitized

def get_system_context() -> Dict[str, Any]:
    """Get system context information for logging"""
    try:
        import psutil
        import platform
        
        return {
            'hostname': platform.node(),
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
    except ImportError:
        # Fallback if psutil is not available
        return {
            'hostname': platform.node() if 'platform' in globals() else 'unknown',
            'platform': platform.system() if 'platform' in globals() else 'unknown'
        }
    except Exception:
        return {'error': 'failed_to_get_system_info'}

def send_security_alert(log_entry: Dict[str, Any]) -> None:
    """Send security alerts for critical events"""
    try:
        # In a real implementation, this would send alerts via:
        # - Email notifications
        # - Slack/Discord webhooks
        # - SMS alerts
        # - Security monitoring systems (SIEM)
        
        alert_message = (
            f"🚨 SECURITY ALERT 🚨\n"
            f"Event: {log_entry['event_type']}\n"
            f"Severity: {log_entry['severity']}\n"
            f"Time: {log_entry['timestamp']}\n"
            f"IP: {log_entry['user_ip']}\n"
            f"Event ID: {log_entry['event_id']}"
        )
        
        # Log the alert (in production, replace with actual alerting)
        security_logger.critical(f"ALERT_TRIGGERED: {alert_message}")
        
    except Exception as e:
        security_logger.error(f"Failed to send security alert: {str(e)}")

def log_malicious_input_detected(input_text: str, threat_details: Dict[str, Any], user_ip: str) -> bool:
    """Convenience function for logging malicious input detection"""
    return log_security_event(
        event_type="malicious_input_detected",
        details={
            'input_text': input_text[:200] + '...' if len(input_text) > 200 else input_text,
            'threat_analysis': threat_details,
            'input_length': len(input_text)
        },
        severity="warning",
        user_ip=user_ip
    )

def log_search_query(query: str, user_ip: str, results_count: int) -> bool:
    """Log search queries for analytics and monitoring"""
    return log_security_event(
        event_type="search_query",
        details={
            'query': query,
            'results_count': results_count,
            'query_length': len(query)
        },
        severity="info",
        user_ip=user_ip
    )

def log_api_access(endpoint: str, method: str, user_ip: str, response_code: int) -> bool:
    """Log API access for monitoring"""
    severity = "warning" if response_code >= 400 else "info"
    
    return log_security_event(
        event_type="api_access",
        details={
            'endpoint': endpoint,
            'method': method,
            'response_code': response_code
        },
        severity=severity,
        user_ip=user_ip
    )

# Usage examples
# Log malicious input detection
log_malicious_input_detected(
    "SELECT * FROM users; DROP TABLE users;",
    {'threat_level': 'high', 'patterns': ['sql_injection']},
    "192.168.1.100"
)

# Log search query
log_search_query("action games", "192.168.1.100", 25)

# Log API access
log_api_access("/api/v1/search/games", "POST", "192.168.1.100", 200)

# Log custom security event
log_security_event(
    "suspicious_activity",
    {
        'activity': 'multiple_failed_requests',
        'count': 10,
        'time_window': '60_seconds'
    },
    severity="error",
    user_ip="192.168.1.100"
)
```

### Notes
- Implements structured JSON logging for easy parsing and analysis
- Automatically sanitizes sensitive information from logs
- Provides system context information for comprehensive monitoring
- Includes alerting mechanism for critical security events
- Supports multiple severity levels with appropriate handling
- Includes convenience functions for common security events
- Generates unique event IDs for tracking and correlation

### Related Functions
- [detect_malicious_patterns](#detect_malicious_patterns)
- [sanitize_input](#sanitize_input)
- [validate_search_query](#validate_search_query)

### Tags
#logging #security #monitoring #alerts #structured-logging #audit-trail
