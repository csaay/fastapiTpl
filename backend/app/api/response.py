"""
统一 API 响应工具函数
"""

from typing import TypeVar

from app.models import ApiResponse, PagedData

T = TypeVar("T")


def success(data: T | None = None, message: str = "success") -> ApiResponse[T]:
    """
    创建成功响应

    Args:
        data: 响应数据
        message: 响应消息

    Returns:
        统一响应对象
    """
    return ApiResponse(code=200, message=message, data=data)


def error(code: int = 400, message: str = "error") -> ApiResponse[None]:
    """
    创建错误响应

    Args:
        code: 错误码
        message: 错误消息

    Returns:
        统一响应对象
    """
    return ApiResponse(code=code, message=message, data=None)


def paged_response(
    items: list[T],
    total: int,
    page: int = 1,
    page_size: int = 20,
    message: str = "success",
) -> ApiResponse[PagedData[T]]:
    """
    创建分页响应

    Args:
        items: 当前页数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页数量
        message: 响应消息

    Returns:
        统一的分页响应对象
    """
    pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ApiResponse(
        code=200,
        message=message,
        data=PagedData(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        ),
    )
