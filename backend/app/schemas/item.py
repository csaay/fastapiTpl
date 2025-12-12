"""
Item 相关的请求/响应模型
"""
import uuid

from sqlmodel import Field, SQLModel


class ItemCreate(SQLModel):
    """Item 创建请求"""
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ItemUpdate(SQLModel):
    """Item 更新请求"""
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ItemPublic(SQLModel):
    """Item 公开信息响应"""
    id: uuid.UUID
    title: str
    description: str | None = None
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    """Item 列表响应（旧版兼容）"""
    data: list[ItemPublic]
    count: int
