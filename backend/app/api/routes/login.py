"""
登录相关路由
"""
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.api.response import success
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import ApiResponse, NewPassword, Token, UserPublic
from app.repositories import user_repository
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])


@router.post("/login/access-token", response_model=ApiResponse[Token])
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Any:
    """
    OAuth2 兼容的 token 登录，获取访问令牌
    """
    user = user_repository.authenticate(
        session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )
    return success(data=token)


@router.post("/login/test-token", response_model=ApiResponse[UserPublic])
def test_token(current_user: CurrentUser) -> Any:
    """
    测试访问令牌
    """
    return success(data=current_user)


@router.post("/password-recovery/{email}", response_model=ApiResponse[None])
def recover_password(email: str, session: SessionDep) -> Any:
    """
    密码恢复
    """
    user = user_repository.get_by_email(session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return success(message="Password recovery email sent")


@router.post("/reset-password/", response_model=ApiResponse[None])
def reset_password(session: SessionDep, body: NewPassword) -> Any:
    """
    重置密码
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = user_repository.get_by_email(session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return success(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    获取密码恢复邮件的 HTML 内容
    """
    user = user_repository.get_by_email(session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
