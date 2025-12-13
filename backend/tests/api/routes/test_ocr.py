"""
OCR 接口测试
"""
import io

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from app.core.config import settings


def create_test_image_with_text() -> bytes:
    """创建包含文字的测试图片"""
    img = Image.new("RGB", (200, 100), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 40), "Hello 你好", fill="black")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def create_blank_image() -> bytes:
    """创建空白测试图片（无文字）"""
    img = Image.new("RGB", (100, 100), color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def test_ocr_recognize_image(client: TestClient) -> None:
    """测试：上传有效图片，返回识别结果"""
    image_bytes = create_test_image_with_text()
    
    response = client.post(
        f"{settings.API_V1_STR}/ocr/recognize",
        files={"file": ("test.png", image_bytes, "image/png")},
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["code"] == 200
    assert "data" in content
    assert "sim_number" in content["data"]


def test_ocr_recognize_invalid_file_type(client: TestClient) -> None:
    """测试：上传非图片文件，返回 400 错误"""
    response = client.post(
        f"{settings.API_V1_STR}/ocr/recognize",
        files={"file": ("test.txt", b"hello world", "text/plain")},
    )
    
    assert response.status_code == 400
    content = response.json()
    assert content["code"] == 400
    assert "不支持的文件类型" in content["message"]


def test_ocr_recognize_empty_file(client: TestClient) -> None:
    """测试：上传空文件，返回 400 错误"""
    response = client.post(
        f"{settings.API_V1_STR}/ocr/recognize",
        files={"file": ("test.png", b"", "image/png")},
    )
    
    assert response.status_code == 400
    content = response.json()
    assert content["code"] == 400
    assert "文件为空" in content["message"]


def test_ocr_recognize_image_no_text(client: TestClient) -> None:
    """测试：上传无文字图片，返回空结果"""
    image_bytes = create_blank_image()
    
    response = client.post(
        f"{settings.API_V1_STR}/ocr/recognize",
        files={"file": ("blank.png", image_bytes, "image/png")},
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["code"] == 200
    # 无文字图片应返回空字符串
    assert content["data"]["sim_number"] == ""
