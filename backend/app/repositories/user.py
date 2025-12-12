"""
User Repository

用户数据访问层
"""
import uuid

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """用户 Repository"""
    
    def __init__(self):
        super().__init__(User)
    
    def create(self, session: Session, *, obj_in: UserCreate) -> User:
        """创建用户（密码加密）"""
        db_obj = User.model_validate(
            obj_in,
            update={"hashed_password": get_password_hash(obj_in.password)}
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update(
        self, session: Session, *, db_obj: User, obj_in: UserUpdate
    ) -> User:
        """更新用户（密码加密）"""
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def get_by_email(self, session: Session, *, email: str) -> User | None:
        """根据邮箱获取用户"""
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()
    
    def authenticate(
        self, session: Session, *, email: str, password: str
    ) -> User | None:
        """验证用户凭据"""
        user = self.get_by_email(session, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


# 单例实例
user_repository = UserRepository()
