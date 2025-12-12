"""
User 数据库模型
"""
import uuid
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.item import Item


class UserBase(SQLModel):
    """用户基础属性"""
    email: str = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class User(UserBase, table=True):
    """用户数据库模型"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: List["Item"] = Relationship(back_populates="owner", cascade_delete=True)
