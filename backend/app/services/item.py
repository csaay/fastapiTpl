"""
Item 服务

处理 Item 相关的业务逻辑
"""
import logging
import uuid

from sqlmodel import Session

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models import Item, User
from app.schemas import  ItemUpdate
from app.repositories import item_repository

logger = logging.getLogger(__name__)


class ItemService:
    """Item 服务"""
    

    def get_item(self, session: Session, *, item_id: uuid.UUID) -> Item:
        """
        获取 Item
        
        Raises:
            NotFoundError: Item 不存在
        """
        item = item_repository.get(session, item_id)
        if not item:
            raise NotFoundError(f"Item {item_id} not found")
        return item
    
    def get_item_with_permission(
        self,
        session: Session,
        *,
        item_id: uuid.UUID,
        current_user: User,
    ) -> Item:
        """
        获取 Item（检查权限）
        
        Raises:
            NotFoundError: Item 不存在
            ForbiddenError: 没有权限
        """
        item = self.get_item(session, item_id=item_id)
        
        if not current_user.is_superuser and item.owner_id != current_user.id:
            raise ForbiddenError("Not enough permissions")
        
        return item
    
    def update_item(
        self,
        session: Session,
        *,
        item_id: uuid.UUID,
        item_in: ItemUpdate,
        current_user: User,
    ) -> Item:
        """
        更新 Item
        
        Raises:
            NotFoundError: Item 不存在
            ForbiddenError: 没有权限
        """
        item = self.get_item_with_permission(
            session, item_id=item_id, current_user=current_user
        )
        
        update_data = item_in.model_dump(exclude_unset=True)
        item.sqlmodel_update(update_data)
        session.add(item)
        session.commit()
        session.refresh(item)
        
        logger.info("Item updated: %s", item.title)
        return item
    
    def delete_item(
        self,
        session: Session,
        *,
        item_id: uuid.UUID,
        current_user: User,
    ) -> None:
        """
        删除 Item
        
        Raises:
            NotFoundError: Item 不存在
            ForbiddenError: 没有权限
        """
        item = self.get_item_with_permission(
            session, item_id=item_id, current_user=current_user
        )
        
        item_repository.delete(session, id=item_id)
        logger.info("Item deleted: %s", item.title)


# 单例实例
item_service = ItemService()
