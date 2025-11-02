"""
Steam Game Search Engine - Application Entry Point
Steam游戏搜索引擎应用程序入口点

This is the main entry point for the Steam Game Search Engine application.
这是Steam游戏搜索引擎应用程序的主要入口点。
"""

import uvicorn
import logging
from app import app, get_settings

# 获取配置 / Get configuration
settings = get_settings()

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    """
    应用程序启动入口
    Application startup entry point.
    
    启动FastAPI应用程序服务器。
    Starts the FastAPI application server.
    """
    logger.info(f"🚀 Starting Steam Game Search Engine on {settings.host}:{settings.port}")
    logger.info(f"🔧 Environment: {settings.environment}")
    logger.info(f"🐛 Debug mode: {settings.debug}")
    
    # 启动服务器 / Start server
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
        workers=1 if settings.debug else 4
    )
