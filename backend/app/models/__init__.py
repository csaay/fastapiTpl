"""
Models 模块

统一导出所有数据库模型和 schemas（保持向后兼容）
"""
# 数据库模型
from app.models.user import User, UserBase
from app.models.item import Item, ItemBase

# 请求/响应模型（从 schemas 导入以保持向后兼容）
from app.schemas.common import ApiResponse, Message, PagedData
from app.schemas.user import (
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    UpdatePassword,
)
from app.schemas.item import (
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
)
from app.schemas.token import (
    Token,
    TokenPayload,
    NewPassword,
)

__all__ = [
    # Database models
    "User",
    "UserBase",
    "Item",
    "ItemBase",
    # Schemas (backward compatible)
    "ApiResponse",
    "Message",
    "PagedData",
    "UserCreate",
    "UserPublic",
    "UserRegister",
    "UsersPublic",
    "UserUpdate",
    "UserUpdateMe",
    "UpdatePassword",
    "ItemCreate",
    "ItemPublic",
    "ItemsPublic",
    "ItemUpdate",
    "Token",
    "TokenPayload",
    "NewPassword",
]
