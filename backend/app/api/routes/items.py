import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.api.response import paged_response, success
from app.models import (
    ApiResponse,
    Item,
    ItemCreate,
    ItemPublic,
    ItemUpdate,
    PagedData,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ApiResponse[PagedData[ItemPublic]])
def read_items(
    session: SessionDep,
    current_user: CurrentUser,
    page: int = 1,
    page_size: int = 20,
) -> Any:
    """
    获取 Item 列表（分页）
    """
    # 计算偏移量
    skip = (page - 1) * page_size

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        total = session.exec(count_statement).one()
        statement = select(Item).offset(skip).limit(page_size)
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == current_user.id)
        )
        total = session.exec(count_statement).one()
        statement = (
            select(Item)
            .where(Item.owner_id == current_user.id)
            .offset(skip)
            .limit(page_size)
        )
        items = session.exec(statement).all()

    return paged_response(items=list(items), total=total, page=page, page_size=page_size)


@router.get("/{id}", response_model=ApiResponse[ItemPublic])
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    根据 ID 获取 Item
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return success(data=item)


@router.post("/", response_model=ApiResponse[ItemPublic])
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    创建新 Item
    """
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return success(data=item)


@router.put("/{id}", response_model=ApiResponse[ItemPublic])
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    更新 Item
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return success(data=item)


@router.delete("/{id}", response_model=ApiResponse[None])
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    删除 Item
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(item)
    session.commit()
    return success(message="Item deleted successfully")
