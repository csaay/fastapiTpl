"""
通用响应模型
"""
from typing import Generic, TypeVar

from sqlmodel import SQLModel

T = TypeVar("T")


class Message(SQLModel):
    """通用消息响应"""
    message: str


class PagedData(SQLModel, Generic[T]):
    """分页数据结构"""
    items: list[T]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int = 0


class ApiResponse(SQLModel, Generic[T]):
    """统一 API 响应模型"""
    code: int = 200
    message: str = "success"
    data: T | None = None
