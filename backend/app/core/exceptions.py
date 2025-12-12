"""
自定义异常类

提供应用程序的统一异常处理
"""


class AppException(Exception):
    """应用基础异常"""
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class NotFoundError(AppException):
    """资源不存在 (404)"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, message)


class UnauthorizedError(AppException):
    """未授权 (401)"""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(401, message)


class ForbiddenError(AppException):
    """权限不足 (403)"""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(403, message)


class BadRequestError(AppException):
    """请求错误 (400)"""
    
    def __init__(self, message: str = "Bad request"):
        super().__init__(400, message)


class ConflictError(AppException):
    """资源冲突 (409)"""
    
    def __init__(self, message: str = "Conflict"):
        super().__init__(409, message)


class InternalServerError(AppException):
    """服务器内部错误 (500)"""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(500, message)
