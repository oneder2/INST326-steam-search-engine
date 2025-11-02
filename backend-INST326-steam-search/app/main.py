"""
Steam Game Search Engine - FastAPI Application
Steam游戏搜索引擎 - FastAPI应用程序

This is the main FastAPI application entry point with modular architecture.
这是采用模块化架构的主要FastAPI应用程序入口点。
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from typing import Optional

# 导入配置和核心组件 / Import configuration and core components
from .config.settings import get_settings
from .core import get_search_engine, GameSearchEngine
from .utils.logging import setup_logging, log_api_request
from .api.routes import search_router, games_router, health_router

# 获取配置 / Get configuration
settings = get_settings()

# 设置日志 / Setup logging
setup_logging(settings.log_level, settings.log_format)
logger = logging.getLogger(__name__)

# 全局搜索引擎实例 / Global search engine instance
search_engine: Optional[GameSearchEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用程序生命周期管理器
    Application lifespan manager for startup and shutdown events.
    
    管理应用程序的启动和关闭逻辑，包括搜索引擎初始化和清理。
    Manages application startup and shutdown logic including search engine initialization and cleanup.
    """
    # 启动逻辑 / Startup logic
    logger.info("🚀 Steam Game Search Engine API starting up...")
    
    global search_engine
    try:
        # 初始化搜索引擎 / Initialize search engine
        search_engine = get_search_engine()
        await search_engine.initialize()
        
        logger.info("✅ GameSearchEngine initialized successfully!")
        
        # 打印可用端点信息 / Print available endpoints info
        print("\n📋 Available endpoints:")
        print("🔍 API documentation: /docs")
        print("📚 Alternative docs: /redoc")
        print("❤️  Health check: /api/v1/health")
        print("🔎 Search games: POST /api/v1/search/games")
        print("💡 Search suggestions: GET /api/v1/search/suggest")
        print("🎮 Game details: GET /api/v1/games/{game_id}")
        print(f"\n🌐 Server running on {settings.host}:{settings.port}")
        print(f"🔧 Environment: {settings.environment}")
        print(f"🐛 Debug mode: {settings.debug}\n")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")
        logger.warning("⚠️  Search engine initialization failed")
        search_engine = None
    
    yield  # 应用程序运行期间 / During application runtime
    
    # 关闭逻辑 / Shutdown logic
    logger.info("🛑 Steam Game Search Engine API shutting down...")
    if search_engine:
        try:
            await search_engine.shutdown()
            logger.info("✅ GameSearchEngine shutdown completed")
        except Exception as e:
            logger.error(f"❌ Shutdown error: {str(e)}")


# 创建FastAPI应用实例 / Create FastAPI application instance
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=settings.debug
)


# CORS中间件配置 / CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# 请求日志中间件 / Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    请求日志中间件
    Request logging middleware for API request tracking.
    
    记录所有API请求的详细信息，包括响应时间和状态码。
    Logs detailed information for all API requests including response time and status code.
    """
    start_time = time.time()
    
    # 获取客户端信息 / Get client information
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # 处理请求 / Process request
    response = await call_next(request)
    
    # 计算处理时间 / Calculate processing time
    process_time = time.time() - start_time
    
    # 记录请求日志 / Log request
    log_api_request(
        method=request.method,
        path=str(request.url.path),
        status_code=response.status_code,
        duration=process_time,
        client_ip=client_ip,
        user_agent=user_agent,
        query_params=dict(request.query_params)
    )
    
    # 添加响应头 / Add response headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-API-Version"] = settings.api_version
    
    return response


# 全局异常处理器 / Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    Global exception handler for unhandled errors.
    
    处理所有未捕获的异常，返回标准化的错误响应。
    Handles all unhandled exceptions and returns standardized error responses.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": time.time(),
            "request_id": getattr(request.state, 'request_id', None)
        }
    )


# 注册API路由 / Register API routes
app.include_router(
    search_router,
    prefix="/api/v1",
    tags=["search"]
)

app.include_router(
    games_router,
    prefix="/api/v1",
    tags=["games"]
)

app.include_router(
    health_router,
    prefix="/api/v1",
    tags=["health"]
)


# 根路径端点 / Root path endpoint
@app.get("/", tags=["root"])
async def root():
    """
    根路径端点
    Root path endpoint with API information.
    
    返回API基本信息和可用端点列表。
    Returns basic API information and available endpoints list.
    """
    return {
        "message": "Steam Game Search Engine API",
        "version": settings.api_version,
        "status": "running",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "health": "/api/v1/health",
            "search": "/api/v1/search/games",
            "suggestions": "/api/v1/search/suggest",
            "game_detail": "/api/v1/games/{game_id}"
        },
        "timestamp": time.time()
    }


# 开发服务器启动 / Development server startup
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting development server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )
