"""
Services 模块

统一导出所有服务
"""
from app.services.auth import AuthService, auth_service
from app.services.user import UserService, user_service
from app.services.item import ItemService, item_service

__all__ = [
    "AuthService",
    "auth_service",
    "UserService",
    "user_service",
    "ItemService",
    "item_service",
]
