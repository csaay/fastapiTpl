"""
Item Repository

Item 数据访问层
"""
import uuid

from sqlmodel import Session, select, func

from app.models import Item
from app.schemas import ItemCreate, ItemUpdate
from app.repositories.base import BaseRepository


class ItemRepository(BaseRepository[Item, ItemCreate, ItemUpdate]):
    """Item Repository"""
    
    def __init__(self):
        super().__init__(Item)
    
    def create_with_owner(
        self, session: Session, *, obj_in: ItemCreate, owner_id: uuid.UUID
    ) -> Item:
        """创建 Item（指定所有者）"""
        db_obj = Item.model_validate(obj_in, update={"owner_id": owner_id})
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def get_multi_by_owner(
        self,
        session: Session,
        *,
        owner_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Item], int]:
        """获取指定用户的 Items（分页）"""
        offset = (page - 1) * page_size
        
        # 获取总数
        count_statement = select(func.count()).select_from(Item).where(Item.owner_id == owner_id)
        total = session.exec(count_statement).one()
        
        # 获取分页数据
        statement = (
            select(Item)
            .where(Item.owner_id == owner_id)
            .offset(offset)
            .limit(page_size)
        )
        items = list(session.exec(statement).all())
        
        return items, total


# 单例实例
item_repository = ItemRepository()
