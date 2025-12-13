"""
OCR 路由

提供图片文字识别接口
"""
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile

from app.api.response import success
from app.models import ApiResponse
from app.schemas.ocr import OcrSimResult
from app.services.ocr import ocr_service

router = APIRouter(prefix="/ocr", tags=["ocr"])

# 允许的图片格式
ALLOWED_CONTENT_TYPES: set[str] = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/bmp",
    "image/webp",
}


@router.post("/recognize", response_model=ApiResponse[OcrSimResult])
async def recognize_image(file: UploadFile) -> Any:
    """
    识别图片中的文字
    
    上传图片，返回识别出的文字内容。
    
    支持格式: jpg, jpeg, png, bmp, webp
    """
    # 校验文件类型
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}，仅支持 jpg/png/bmp/webp"
        )

    # 读取文件内容
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="上传的文件为空")

    # 调用 OCR 服务
    ocr_result = ocr_service.get_sim(content)

    return success(data=ocr_result)
