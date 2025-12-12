from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.api.response import success
from app.models import ApiResponse
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
    response_model=ApiResponse[None],
)
def test_email(email_to: EmailStr) -> ApiResponse[None]:
    """
    测试邮件发送
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return success(message="Test email sent")


@router.get("/health-check/", response_model=ApiResponse[bool])
async def health_check() -> ApiResponse[bool]:
    """
    健康检查
    """
    return success(data=True)
