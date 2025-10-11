# validate_configuration

## validate_configuration

**Category:** Configuration
**Complexity:** Medium
**Last Updated:** 2024-10-11

### Description
Validates application configuration settings to ensure all required parameters are properly set and accessible. Performs comprehensive checks on file paths, network settings, and feature flags to prevent runtime errors.

### Signature
```python
def validate_configuration(settings: Settings) -> bool:
```

### Parameters
- `settings` (Settings, required): Settings object to validate

### Returns
- `bool`: True if configuration is valid, False otherwise

### Example
```python
import os
import socket
from pathlib import Path
from typing import List, Tuple

def validate_configuration(settings: Settings) -> bool:
    """
    Comprehensive validation of application configuration
    """
    validation_results = []
    
    # Validate server configuration
    validation_results.append(validate_server_config(settings))
    
    # Validate database configuration
    validation_results.append(validate_database_config(settings))
    
    # Validate search configuration
    validation_results.append(validate_search_config(settings))
    
    # Validate file paths
    validation_results.append(validate_file_paths(settings))
    
    # Check if all validations passed
    all_valid = all(validation_results)
    
    if all_valid:
        logger.info("✅ All configuration validations passed")
    else:
        logger.error("❌ Configuration validation failed")
    
    return all_valid

def validate_server_config(settings: Settings) -> bool:
    """Validate server-related configuration"""
    try:
        # Check port range
        if not (1 <= settings.port <= 65535):
            logger.error(f"Invalid port number: {settings.port}")
            return False
        
        # Check if port is available
        if not is_port_available(settings.host, settings.port):
            logger.warning(f"Port {settings.port} may not be available")
        
        # Validate host format
        if settings.host not in ["0.0.0.0", "localhost", "127.0.0.1"]:
            try:
                socket.inet_aton(settings.host)
            except socket.error:
                logger.error(f"Invalid host address: {settings.host}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Server config validation error: {str(e)}")
        return False

def validate_database_config(settings: Settings) -> bool:
    """Validate database configuration"""
    try:
        # Check database URL format
        if not settings.database_url.startswith("sqlite:///"):
            logger.error("Only SQLite databases are currently supported")
            return False
        
        # Check database directory exists
        db_path = settings.database_url.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        
        if db_dir and not os.path.exists(db_dir):
            logger.warning(f"Database directory does not exist: {db_dir}")
            # Try to create directory
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
            except Exception as e:
                logger.error(f"Cannot create database directory: {str(e)}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Database config validation error: {str(e)}")
        return False

def validate_search_config(settings: Settings) -> bool:
    """Validate search-related configuration"""
    try:
        # Check that at least one search method is enabled
        if not (settings.enable_bm25_search or settings.enable_semantic_search):
            logger.error("At least one search method must be enabled")
            return False
        
        # Validate search limits
        if settings.max_search_results <= 0:
            logger.error("max_search_results must be positive")
            return False
        
        if settings.default_search_limit <= 0:
            logger.error("default_search_limit must be positive")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Search config validation error: {str(e)}")
        return False

def validate_file_paths(settings: Settings) -> bool:
    """Validate required file paths"""
    try:
        paths_to_check = []
        
        if settings.enable_semantic_search:
            paths_to_check.append(("Faiss index", settings.faiss_index_path))
        
        if settings.enable_bm25_search:
            paths_to_check.append(("BM25 index", settings.bm25_index_path))
        
        all_exist = True
        for name, path in paths_to_check:
            if not os.path.exists(path):
                logger.warning(f"{name} file not found: {path}")
                all_exist = False
        
        return True  # Don't fail validation for missing index files
    except Exception as e:
        logger.error(f"File path validation error: {str(e)}")
        return False

def is_port_available(host: str, port: int) -> bool:
    """Check if a port is available for binding"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # Port is available if connection fails
    except Exception:
        return False

# Usage example
settings = get_settings()
if validate_configuration(settings):
    print("Configuration is valid, starting application...")
else:
    print("Configuration validation failed, please check settings")
```

### Notes
- Performs comprehensive validation of all configuration aspects
- Checks network connectivity and port availability
- Validates file system paths and permissions
- Provides detailed error messages for troubleshooting
- Non-blocking validation for optional components
- Includes automatic directory creation for missing paths

### Related Functions
- [get_settings](#get_settings)
- [load_environment_variables](#load_environment_variables)
- [print_startup_info](#print_startup_info)

### Tags
#validation #configuration #startup #error-checking #network #filesystem
