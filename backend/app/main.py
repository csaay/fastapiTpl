import sentry_sdk
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.api.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging, get_logger

# 初始化日志系统
setup_logging()
logger = get_logger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# CORS 中间件
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# ==================== 异常处理器 ====================

# 自定义应用异常
app.add_exception_handler(AppException, app_exception_handler)

# HTTP 异常
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """将 HTTPException 统一包装为标准响应格式"""
    logger.warning("HTTPException: %s - %s | Path: %s", exc.status_code, exc.detail, request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )

# 请求验证异常
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 未处理异常（生产环境）
if settings.ENVIRONMENT != "local":
    app.add_exception_handler(Exception, unhandled_exception_handler)

logger.info("Application started | Environment: %s", settings.ENVIRONMENT)
