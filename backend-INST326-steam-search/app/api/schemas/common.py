"""
Steam Game Search Engine - Common API Schemas
通用API数据模式定义

This module contains common Pydantic models used across different API endpoints.
该模块包含跨不同API端点使用的通用Pydantic模型。
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    """
    响应状态枚举
    Response status enumeration for API responses.
    """
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ErrorResponse(BaseModel):
    """
    错误响应模型
    Error response model for API error handling.
    
    用于API错误处理的标准错误响应模型。
    Standard error response model for API error handling.
    """
    status: ResponseStatus = Field(default=ResponseStatus.ERROR, description="响应状态")
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(None, description="错误代码")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详细信息")
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp(), description="时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Invalid search query",
                "error_code": "INVALID_QUERY",
                "details": {
                    "field": "query",
                    "reason": "Query cannot be empty"
                },
                "timestamp": 1634567890.123,
                "request_id": "req_12345"
            }
        }


class SuccessResponse(BaseModel):
    """
    成功响应模型
    Success response model for API operations.
    
    用于API操作的标准成功响应模型。
    Standard success response model for API operations.
    """
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="响应状态")
    message: str = Field(..., description="成功消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp(), description="时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {
                    "result": "success",
                    "count": 10
                },
                "timestamp": 1634567890.123,
                "request_id": "req_12345"
            }
        }


class PaginationInfo(BaseModel):
    """
    分页信息模型
    Pagination information model for paginated responses.
    
    用于分页响应的分页信息模型。
    Pagination information model for paginated responses.
    """
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, le=100, description="每页项目数")
    total_items: int = Field(..., ge=0, description="总项目数")
    total_pages: int = Field(..., ge=0, description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_previous: bool = Field(..., description="是否有上一页")
    
    @validator('total_pages', always=True)
    def calculate_total_pages(cls, v, values):
        """计算总页数 / Calculate total pages"""
        if 'total_items' in values and 'page_size' in values:
            total_items = values['total_items']
            page_size = values['page_size']
            return (total_items + page_size - 1) // page_size
        return v
    
    @validator('has_next', always=True)
    def calculate_has_next(cls, v, values):
        """计算是否有下一页 / Calculate if has next page"""
        if 'page' in values and 'total_pages' in values:
            return values['page'] < values['total_pages']
        return v
    
    @validator('has_previous', always=True)
    def calculate_has_previous(cls, v, values):
        """计算是否有上一页 / Calculate if has previous page"""
        if 'page' in values:
            return values['page'] > 1
        return v
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "page": 2,
                "page_size": 20,
                "total_items": 150,
                "total_pages": 8,
                "has_next": True,
                "has_previous": True
            }
        }


class PaginatedResponse(BaseModel):
    """
    分页响应模型
    Paginated response model for list endpoints.
    
    用于列表端点的分页响应模型。
    Paginated response model for list endpoints.
    """
    items: List[Dict[str, Any]] = Field(default_factory=list, description="项目列表")
    pagination: PaginationInfo = Field(..., description="分页信息")
    filters: Optional[Dict[str, Any]] = Field(None, description="应用的过滤器")
    sort: Optional[Dict[str, str]] = Field(None, description="排序信息")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "items": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"}
                ],
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total_items": 100,
                    "total_pages": 5,
                    "has_next": True,
                    "has_previous": False
                },
                "filters": {"category": "games"},
                "sort": {"field": "name", "order": "asc"}
            }
        }


class ValidationError(BaseModel):
    """
    验证错误模型
    Validation error model for input validation errors.
    
    用于输入验证错误的验证错误模型。
    Validation error model for input validation errors.
    """
    field: str = Field(..., description="错误字段")
    message: str = Field(..., description="错误消息")
    invalid_value: Optional[Union[str, int, float, bool]] = Field(None, description="无效值")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "field": "price",
                "message": "Price must be greater than or equal to 0",
                "invalid_value": -10
            }
        }


class ValidationErrorResponse(BaseModel):
    """
    验证错误响应模型
    Validation error response model for input validation failures.
    
    用于输入验证失败的验证错误响应模型。
    Validation error response model for input validation failures.
    """
    status: ResponseStatus = Field(default=ResponseStatus.ERROR, description="响应状态")
    message: str = Field(default="Validation failed", description="错误消息")
    errors: List[ValidationError] = Field(..., description="验证错误列表")
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp(), description="时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Validation failed",
                "errors": [
                    {
                        "field": "query",
                        "message": "Query cannot be empty",
                        "invalid_value": ""
                    },
                    {
                        "field": "limit",
                        "message": "Limit must be between 1 and 100",
                        "invalid_value": 150
                    }
                ],
                "timestamp": 1634567890.123,
                "request_id": "req_12345"
            }
        }


class MetaInfo(BaseModel):
    """
    元信息模型
    Meta information model for API responses.
    
    用于API响应的元信息模型。
    Meta information model for API responses.
    """
    version: str = Field(..., description="API版本")
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp(), description="响应时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")
    processing_time: Optional[float] = Field(None, ge=0, description="处理时间（秒）")
    server_info: Optional[Dict[str, str]] = Field(None, description="服务器信息")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "version": "2.0.0",
                "timestamp": 1634567890.123,
                "request_id": "req_12345",
                "processing_time": 0.125,
                "server_info": {
                    "environment": "production",
                    "region": "us-east-1"
                }
            }
        }


class ApiResponse(BaseModel):
    """
    通用API响应模型
    Generic API response model with meta information.
    
    包含元信息的通用API响应模型。
    Generic API response model with meta information.
    """
    data: Optional[Union[Dict[str, Any], List[Any]]] = Field(None, description="响应数据")
    meta: MetaInfo = Field(..., description="元信息")
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="响应状态")
    message: Optional[str] = Field(None, description="响应消息")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "data": {
                    "results": [],
                    "total": 0
                },
                "meta": {
                    "version": "2.0.0",
                    "timestamp": 1634567890.123,
                    "processing_time": 0.125
                },
                "status": "success",
                "message": "Request processed successfully"
            }
        }


class SortOption(BaseModel):
    """
    排序选项模型
    Sort option model for sorting parameters.
    
    用于排序参数的排序选项模型。
    Sort option model for sorting parameters.
    """
    field: str = Field(..., description="排序字段")
    order: str = Field(default="asc", pattern="^(asc|desc)$", description="排序顺序")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "field": "title",
                "order": "asc"
            }
        }


class FilterOption(BaseModel):
    """
    过滤选项模型
    Filter option model for filtering parameters.
    
    用于过滤参数的过滤选项模型。
    Filter option model for filtering parameters.
    """
    field: str = Field(..., description="过滤字段")
    operator: str = Field(..., description="过滤操作符")
    value: Union[str, int, float, bool, List[Any]] = Field(..., description="过滤值")
    
    class Config:
        """Pydantic配置 / Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "field": "price",
                "operator": "lte",
                "value": 50.0
            }
        }
