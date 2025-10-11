# get_settings

## get_settings

**Category:** Configuration
**Complexity:** Medium
**Last Updated:** 2024-10-11

### Description
Retrieves and validates application settings from environment variables and configuration files. Implements the singleton pattern to ensure consistent configuration access across the application with proper validation and type conversion.

### Signature
```python
def get_settings() -> Settings:
```

### Parameters
None

### Returns
- `Settings`: Validated settings object with all configuration parameters

### Example
```python
from functools import lru_cache
from pydantic import BaseSettings, Field
from typing import List, Optional

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8000, description="Server port number")
    debug: bool = Field(default=False, description="Debug mode flag")
    
    # Database configuration
    database_url: str = Field(default="sqlite:///data/games_data.db")
    database_timeout: float = Field(default=30.0)
    
    # Search configuration
    enable_bm25_search: bool = Field(default=True)
    enable_semantic_search: bool = Field(default=True)
    enable_fusion_ranking: bool = Field(default=True)
    
    # API configuration
    api_version: str = Field(default="1.0.0")
    max_search_results: int = Field(default=1000)
    default_search_limit: int = Field(default=20)
    
    # CORS configuration
    cors_origins: str = Field(default="http://localhost:3000")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def validate_paths(self) -> None:
        """Validate that required file paths exist"""
        import os
        paths_to_check = [
            self.faiss_index_path,
            self.bm25_index_path,
            os.path.dirname(self.database_url.replace("sqlite:///", ""))
        ]
        
        for path in paths_to_check:
            if not os.path.exists(path):
                logger.warning(f"Path does not exist: {path}")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching for performance
    """
    try:
        settings = Settings()
        logger.info("✅ Configuration loaded successfully")
        return settings
    except Exception as e:
        logger.error(f"❌ Failed to load configuration: {str(e)}")
        raise

# Usage example
settings = get_settings()
print(f"Server will run on {settings.host}:{settings.port}")
print(f"Debug mode: {settings.debug}")
```

### Notes
- Uses Pydantic BaseSettings for automatic environment variable parsing
- Implements LRU cache for performance optimization
- Provides validation methods for configuration integrity
- Supports .env file loading with proper encoding
- Includes type conversion and default value handling
- Thread-safe singleton pattern implementation

### Related Functions
- [validate_configuration](#validate_configuration)
- [load_environment_variables](#load_environment_variables)
- [print_startup_info](#print_startup_info)

### Tags
#configuration #settings #environment #pydantic #singleton #validation
