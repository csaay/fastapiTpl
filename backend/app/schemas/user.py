"""
用户相关的请求/响应模型
"""
import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    """用户创建请求"""
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserRegister(SQLModel):
    """用户注册请求"""
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(SQLModel):
    """用户更新请求"""
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None
    is_superuser: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdateMe(SQLModel):
    """用户自我更新请求"""
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """密码更新请求"""
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(SQLModel):
    """用户公开信息响应"""
    id: uuid.UUID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


class UsersPublic(SQLModel):
    """用户列表响应（旧版兼容）"""
    data: list[UserPublic]
    count: int
