"""
Repository 基类

提供通用的 CRUD 操作
"""
import uuid
from typing import Generic, Type, TypeVar

from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """通用 Repository 基类"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, session: Session, id: uuid.UUID) -> ModelType | None:
        """根据 ID 获取单个记录"""
        return session.get(self.model, id)
    
    def get_multi(
        self,
        session: Session,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ModelType], int]:
        """
        获取分页记录列表
        
        Returns:
            (记录列表, 总数)
        """
        offset = (page - 1) * page_size
        
        # 获取总数
        count_statement = select(self.model)
        total = len(session.exec(count_statement).all())
        
        # 获取分页数据
        statement = select(self.model).offset(offset).limit(page_size)
        items = list(session.exec(statement).all())
        
        return items, total
    
    def create(self, session: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """创建记录"""
        db_obj = self.model.model_validate(obj_in)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update(
        self, session: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """更新记录"""
        update_data = obj_in.model_dump(exclude_unset=True)
        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def delete(self, session: Session, *, id: uuid.UUID) -> ModelType | None:
        """删除记录"""
        obj = session.get(self.model, id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj
