"""
OCR Schema 定义
"""
from pydantic import BaseModel


class OcrTextItem(BaseModel):
    """单条文字识别结果"""
    text: str
    """识别出的文字"""
    confidence: float
    """置信度 (0-1)"""
    position: list[list[int]]
    """文字边界框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]"""


class OcrResult(BaseModel):
    """OCR 完整识别结果"""
    items: list[OcrTextItem]
    """识别出的文字列表"""
    full_text: str
    """所有文字拼接后的完整文本"""

class OcrSimResult(BaseModel):
    """OCR Sim卡号识别结果"""
    sim_number: str
    """识别出的Sim卡号"""