# detect_malicious_patterns

## detect_malicious_patterns

**Category:** Validation
**Complexity:** Medium
**Last Updated:** 2024-10-11

### Description
Detects potentially malicious patterns in user input to prevent security attacks such as SQL injection, XSS, command injection, and other common web vulnerabilities. Implements comprehensive pattern matching and heuristic analysis.

### Signature
```python
def detect_malicious_patterns(input_text: str, strict_mode: bool = False) -> Dict[str, Any]:
```

### Parameters
- `input_text` (str, required): User input text to analyze
- `strict_mode` (bool, optional): Enable stricter detection rules (default: False)

### Returns
- `Dict[str, Any]`: Detection results with threat level and details

### Example
```python
import re
from typing import Dict, List, Any, Tuple
from urllib.parse import unquote

def detect_malicious_patterns(input_text: str, strict_mode: bool = False) -> Dict[str, Any]:
    """
    Comprehensive malicious pattern detection for security
    """
    if not input_text:
        return {
            'is_malicious': False,
            'threat_level': 'none',
            'detected_patterns': [],
            'risk_score': 0.0
        }
    
    # Decode URL encoding to catch obfuscated attacks
    decoded_text = unquote(input_text).lower()
    
    detected_threats = []
    risk_score = 0.0
    
    # Check for different types of attacks
    sql_threats = _detect_sql_injection(decoded_text, strict_mode)
    xss_threats = _detect_xss_patterns(decoded_text, strict_mode)
    cmd_threats = _detect_command_injection(decoded_text, strict_mode)
    path_threats = _detect_path_traversal(decoded_text, strict_mode)
    script_threats = _detect_script_injection(decoded_text, strict_mode)
    
    # Combine all threats
    all_threats = sql_threats + xss_threats + cmd_threats + path_threats + script_threats
    
    # Calculate overall risk score
    for threat in all_threats:
        risk_score += threat['severity']
        detected_threats.append(threat)
    
    # Determine threat level
    threat_level = _calculate_threat_level(risk_score)
    
    return {
        'is_malicious': len(detected_threats) > 0,
        'threat_level': threat_level,
        'detected_patterns': detected_threats,
        'risk_score': min(risk_score, 10.0),  # Cap at 10.0
        'input_length': len(input_text),
        'analysis_mode': 'strict' if strict_mode else 'normal'
    }

def _detect_sql_injection(text: str, strict_mode: bool) -> List[Dict[str, Any]]:
    """Detect SQL injection patterns"""
    threats = []
    
    # Common SQL injection patterns
    sql_patterns = [
        (r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)", 3.0, "SQL Keywords"),
        (r"(--|#|/\*|\*/)", 2.0, "SQL Comments"),
        (r"(\bor\b.*=.*\bor\b|\band\b.*=.*\band\b)", 4.0, "SQL Boolean Logic"),
        (r"(';|';\s*--|';\s*#)", 5.0, "SQL Statement Termination"),
        (r"(\bxp_cmdshell\b|\bsp_executesql\b)", 5.0, "SQL Stored Procedures"),
        (r"(0x[0-9a-f]+)", 2.0, "Hexadecimal Encoding"),
        (r"(\bcast\b|\bconvert\b|\bchar\b|\bnchar\b)", 1.5, "SQL Type Conversion"),
    ]
    
    if strict_mode:
        # Additional strict patterns
        sql_patterns.extend([
            (r"(\bwhere\b|\bhaving\b|\border\s+by\b)", 1.0, "SQL Clauses"),
            (r"(\binto\b|\bfrom\b|\bjoin\b)", 1.0, "SQL Table Operations"),
            (r"('.*'|\".*\")", 0.5, "Quoted Strings"),
        ])
    
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
    """Detect Cross-Site Scripting (XSS) patterns"""
    threats = []
    
    xss_patterns = [
        (r"<script[^>]*>.*?</script>", 5.0, "Script Tags"),
        (r"javascript:", 4.0, "JavaScript Protocol"),
        (r"on\w+\s*=", 3.0, "Event Handlers"),
        (r"<iframe[^>]*>", 4.0, "Iframe Tags"),
        (r"<object[^>]*>", 3.0, "Object Tags"),
        (r"<embed[^>]*>", 3.0, "Embed Tags"),
        (r"<link[^>]*>", 2.0, "Link Tags"),
        (r"<meta[^>]*>", 2.0, "Meta Tags"),
        (r"vbscript:", 4.0, "VBScript Protocol"),
        (r"data:.*base64", 3.0, "Data URI with Base64"),
    ]
    
    if strict_mode:
        xss_patterns.extend([
            (r"<\w+[^>]*>", 0.5, "HTML Tags"),
            (r"&\w+;", 0.3, "HTML Entities"),
            (r"eval\s*\(", 2.0, "Eval Function"),
        ])
    
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
    """Detect command injection patterns"""
    threats = []
    
    cmd_patterns = [
        (r"(\||&|;|\$\(|\`)", 3.0, "Command Separators"),
        (r"\b(cat|ls|dir|type|copy|del|rm|mv|cp|chmod|chown)\b", 2.0, "System Commands"),
        (r"\b(wget|curl|nc|netcat|telnet|ssh)\b", 3.0, "Network Commands"),
        (r"\b(python|perl|ruby|php|bash|sh|cmd|powershell)\b", 2.5, "Interpreters"),
        (r"(>|>>|<|2>|2>>)", 2.0, "Redirection Operators"),
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

def _detect_path_traversal(text: str, strict_mode: bool) -> List[Dict[str, Any]]:
    """Detect path traversal patterns"""
    threats = []
    
    path_patterns = [
        (r"(\.\./|\.\.\\)", 4.0, "Directory Traversal"),
        (r"(/etc/passwd|/etc/shadow|/windows/system32)", 5.0, "System File Access"),
        (r"(\\\\|//)", 1.5, "UNC Paths"),
        (r"(%2e%2e%2f|%2e%2e%5c)", 4.0, "Encoded Traversal"),
    ]
    
    for pattern, severity, description in path_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            threats.append({
                'type': 'path_traversal',
                'pattern': description,
                'severity': severity,
                'matches': len(matches),
                'sample': matches[0] if isinstance(matches[0], str) else matches[0][0]
            })
    
    return threats

def _detect_script_injection(text: str, strict_mode: bool) -> List[Dict[str, Any]]:
    """Detect script injection patterns"""
    threats = []
    
    script_patterns = [
        (r"<\?php.*\?>", 4.0, "PHP Code"),
        (r"<%.*%>", 3.0, "ASP Code"),
        (r"{{.*}}", 2.0, "Template Injection"),
        (r"\$\{.*\}", 2.0, "Expression Language"),
        (r"#\{.*\}", 2.0, "SpEL Injection"),
    ]
    
    for pattern, severity, description in script_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            threats.append({
                'type': 'script_injection',
                'pattern': description,
                'severity': severity,
                'matches': len(matches),
                'sample': matches[0][:30] + '...' if len(matches[0]) > 30 else matches[0]
            })
    
    return threats

def _calculate_threat_level(risk_score: float) -> str:
    """Calculate overall threat level based on risk score"""
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

# Usage examples
# Basic detection
result = detect_malicious_patterns("SELECT * FROM users WHERE id = 1; DROP TABLE users;")
# Returns: {'is_malicious': True, 'threat_level': 'high', ...}

# Strict mode detection
result = detect_malicious_patterns("<div onclick='alert(1)'>Click me</div>", strict_mode=True)
# Returns: {'is_malicious': True, 'threat_level': 'medium', ...}

# Safe input
result = detect_malicious_patterns("action adventure games")
# Returns: {'is_malicious': False, 'threat_level': 'none', ...}
```

### Notes
- Implements multiple attack vector detection (SQL, XSS, Command Injection, etc.)
- Uses regex patterns with severity scoring system
- Supports both normal and strict detection modes
- Handles URL encoding and obfuscation attempts
- Provides detailed threat analysis with sample matches
- Configurable threat levels for different security requirements

### Related Functions
- [sanitize_input](#sanitize_input)
- [validate_search_query](#validate_search_query)
- [log_security_event](#log_security_event)

### Tags
#security #validation #sql-injection #xss #command-injection #pattern-matching
