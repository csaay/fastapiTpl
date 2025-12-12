"""
统一异常处理器

将各类异常转换为标准 API 响应格式
"""
import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    处理应用自定义异常
    """
    logger.warning(
        "AppException: %s - %s | Path: %s",
        exc.code, exc.message, request.url.path
    )
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message, "data": None}
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    处理请求验证异常
    """
    errors = exc.errors()
    error_messages = []
    for error in errors:
        loc = ".".join(str(x) for x in error["loc"])
        error_messages.append(f"{loc}: {error['msg']}")
    
    message = "; ".join(error_messages)
    logger.warning("Validation error: %s | Path: %s", message, request.url.path)
    
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": message, "data": None}
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理未捕获的异常
    """
    logger.exception("Unhandled exception | Path: %s | Error: %s", request.url.path, str(exc))
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "Internal server error", "data": None}
    )
