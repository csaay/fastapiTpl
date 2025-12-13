"""
OCR 服务

封装 RapidOCR 调用逻辑，提供图片文字识别功能
"""
from __future__ import annotations

import logging
from io import BytesIO

from PIL import Image
from rapidocr_onnxruntime import RapidOCR

from app.schemas.ocr import OcrResult, OcrTextItem, OcrSimResult

logger = logging.getLogger(__name__)


class OcrService:
    """OCR 服务（单例模式）"""
    
    _instance: OcrService | None = None
    _engine: RapidOCR | None = None
    
    def __new__(cls) -> OcrService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._engine = RapidOCR()
        return cls._instance

    def recognize(self, image_bytes: bytes) -> OcrResult:
        """
        识别图片中的文字
        
        Args:
            image_bytes: 图片字节数据
            
        Returns:
            OcrResult: 识别结果，包含文字列表和完整文本
        """
        # 将字节转为 PIL Image
        image = Image.open(BytesIO(image_bytes))
        
        # 调用 OCR 引擎
        result, _ = self._engine(image)  # type: ignore
        
        items: list[OcrTextItem] = []
        texts: list[str] = []
        
        if result:
            for item in result:
                # item 格式: [position, text, confidence]
                position, text, confidence = item
                items.append(OcrTextItem(
                    text=text,
                    confidence=float(confidence),
                    position=[[int(p[0]), int(p[1])] for p in position]
                ))
                texts.append(text)
        
        full_text = "\n".join(texts)

        return OcrResult(items=items, full_text=full_text)

    def get_sim(self, image_bytes: bytes) -> OcrSimResult:
        """
        识别图片中的sim卡号，只取前20个字母数字字符

        Args:
            image_bytes: 图片字节数据

        Returns:
            str: 识别出的sim卡号字符串
        """
        result = self.recognize(image_bytes)
        final_str = ""
        start = False
        for item in result.items if result.items else []:
            # 寻找第一个数字字符开始
            if not start and item.text[0].isdigit():
                start = True

            if not start:
                continue
            # 仅保留字母数字字符
            if item.text.isalnum():
                final_str += item.text
                if len(final_str) >= 20:
                    break

        return OcrSimResult(sim_number=final_str[:20])




# 单例实例
ocr_service = OcrService()
