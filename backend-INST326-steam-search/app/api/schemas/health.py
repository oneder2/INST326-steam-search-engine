"""
Steam Game Search Engine - Health API Schemas
健康检查API数据模式定义

This module contains Pydantic models for health check and system status API responses.
该模块包含健康检查和系统状态API响应的Pydantic模型。
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from datetime import datetime

from ...config.constants import HealthStatus


class ComponentHealth(BaseModel):
    """
    组件健康状态模型
    Component health status model for individual system components.
    
    用于单个系统组件的健康状态模型。
    Health status model for individual system components.
    """
    status: str = Field(..., description="组件状态")
    details: Optional[Dict[str, Any]] = Field(None, description="组件详细信息")
    last_check: Optional[float] = Field(None, description="最后检查时间戳")
    error: Optional[str] = Field(None, description="错误信息")
    
    @validator('status')
    def validate_status(cls, v):
        """验证状态值 / Validate status value"""
        valid_statuses = [status.value for status in HealthStatus]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "details": {
                    "response_time": 0.05,
                    "last_operation": "search_games"
                },
                "last_check": 1634567890.123,
                "error": None
            }
        }


class PerformanceMetrics(BaseModel):
    """
    性能指标模型
    Performance metrics model for system performance data.
    
    用于系统性能数据的性能指标模型。
    Performance metrics model for system performance data.
    """
    total_requests: int = Field(default=0, ge=0, description="总请求数")
    successful_requests: int = Field(default=0, ge=0, description="成功请求数")
    failed_requests: int = Field(default=0, ge=0, description="失败请求数")
    average_response_time: float = Field(default=0.0, ge=0, description="平均响应时间（秒）")
    uptime_seconds: int = Field(default=0, ge=0, description="运行时间（秒）")
    requests_per_minute: Optional[float] = Field(None, ge=0, description="每分钟请求数")
    
    @validator('successful_requests', 'failed_requests')
    def validate_request_counts(cls, v, values):
        """验证请求计数 / Validate request counts"""
        if 'total_requests' in values:
            total = values['total_requests']
            if v > total:
                raise ValueError("Request count cannot exceed total requests")
        return v
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "total_requests": 1000,
                "successful_requests": 950,
                "failed_requests": 50,
                "average_response_time": 0.125,
                "uptime_seconds": 3600,
                "requests_per_minute": 16.7
            }
        }


class SystemResources(BaseModel):
    """
    系统资源模型
    System resources model for resource utilization data.
    
    用于资源利用率数据的系统资源模型。
    System resources model for resource utilization data.
    """
    cpu_percent: float = Field(..., ge=0, le=100, description="CPU使用率百分比")
    memory_percent: float = Field(..., ge=0, le=100, description="内存使用率百分比")
    disk_percent: Optional[float] = Field(None, ge=0, le=100, description="磁盘使用率百分比")
    load_average: Optional[List[float]] = Field(None, description="系统负载平均值")
    
    @validator('cpu_percent', 'memory_percent', 'disk_percent')
    def round_percentages(cls, v):
        """四舍五入百分比 / Round percentages"""
        if v is not None:
            return round(v, 2)
        return v
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "cpu_percent": 25.5,
                "memory_percent": 68.2,
                "disk_percent": 45.8,
                "load_average": [1.2, 1.5, 1.8]
            }
        }


class HealthResponse(BaseModel):
    """
    健康检查响应模型
    Health check response model for system health status.
    
    用于系统健康状态的健康检查响应模型。
    Health check response model for system health status.
    """
    status: str = Field(..., description="总体健康状态")
    timestamp: int = Field(..., description="检查时间戳")
    services: Dict[str, str] = Field(default_factory=dict, description="服务状态映射")
    version: str = Field(..., description="API版本")
    uptime: int = Field(default=0, ge=0, description="运行时间（秒）")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="性能指标")
    
    @validator('status')
    def validate_overall_status(cls, v):
        """验证总体状态 / Validate overall status"""
        valid_statuses = [status.value for status in HealthStatus]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": 1634567890,
                "services": {
                    "search_engine": "healthy",
                    "data_repository": "healthy",
                    "security_manager": "healthy"
                },
                "version": "2.0.0",
                "uptime": 3600,
                "performance_metrics": {
                    "total_requests": 1000,
                    "average_response_time": 0.125
                }
            }
        }


class SystemStatusResponse(BaseModel):
    """
    系统状态响应模型
    System status response model with comprehensive system information.
    
    包含全面系统信息的系统状态响应模型。
    System status response model with comprehensive system information.
    """
    status: str = Field(..., description="系统状态")
    timestamp: int = Field(..., description="状态时间戳")
    version: str = Field(..., description="API版本")
    environment: str = Field(..., description="运行环境")
    uptime: int = Field(default=0, ge=0, description="运行时间（秒）")
    
    # 组件状态 / Component status
    components: Dict[str, Any] = Field(default_factory=dict, description="组件状态详情")
    
    # 统计信息 / Statistics
    statistics: Dict[str, Any] = Field(default_factory=dict, description="系统统计信息")
    
    # 配置信息 / Configuration
    configuration: Dict[str, Any] = Field(default_factory=dict, description="系统配置信息")
    
    # 系统资源 / System resources
    system_resources: Optional[SystemResources] = Field(None, description="系统资源使用情况")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": 1634567890,
                "version": "2.0.0",
                "environment": "production",
                "uptime": 7200,
                "components": {
                    "search_engine": {
                        "status": "healthy",
                        "details": {"initialized": True}
                    },
                    "data_repository": {
                        "status": "healthy",
                        "details": {"provider": "mock"}
                    }
                },
                "statistics": {
                    "total_searches": 5000,
                    "total_games": 50
                },
                "configuration": {
                    "search_enabled": True,
                    "mock_data_enabled": True
                },
                "system_resources": {
                    "cpu_percent": 25.5,
                    "memory_percent": 68.2
                }
            }
        }


class HealthCheckSummary(BaseModel):
    """
    健康检查摘要模型
    Health check summary model for quick status overview.
    
    用于快速状态概览的健康检查摘要模型。
    Health check summary model for quick status overview.
    """
    overall_status: str = Field(..., description="总体状态")
    healthy_components: int = Field(default=0, ge=0, description="健康组件数")
    total_components: int = Field(default=0, ge=0, description="总组件数")
    degraded_components: int = Field(default=0, ge=0, description="降级组件数")
    unhealthy_components: int = Field(default=0, ge=0, description="不健康组件数")
    last_check: float = Field(..., description="最后检查时间戳")
    
    @validator('healthy_components', 'degraded_components', 'unhealthy_components')
    def validate_component_counts(cls, v, values):
        """验证组件计数 / Validate component counts"""
        if 'total_components' in values:
            total = values['total_components']
            if v > total:
                raise ValueError("Component count cannot exceed total components")
        return v
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "overall_status": "healthy",
                "healthy_components": 4,
                "total_components": 5,
                "degraded_components": 1,
                "unhealthy_components": 0,
                "last_check": 1634567890.123
            }
        }


class ServiceHealth(BaseModel):
    """
    服务健康状态模型
    Service health status model for external service monitoring.
    
    用于外部服务监控的服务健康状态模型。
    Service health status model for external service monitoring.
    """
    service_name: str = Field(..., description="服务名称")
    status: str = Field(..., description="服务状态")
    endpoint: Optional[str] = Field(None, description="服务端点")
    response_time: Optional[float] = Field(None, ge=0, description="响应时间（秒）")
    last_check: float = Field(..., description="最后检查时间戳")
    error_message: Optional[str] = Field(None, description="错误消息")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "service_name": "database",
                "status": "healthy",
                "endpoint": "sqlite:///games.db",
                "response_time": 0.025,
                "last_check": 1634567890.123,
                "error_message": None
            }
        }
