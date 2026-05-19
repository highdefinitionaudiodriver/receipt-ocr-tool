"""Tesseract OCR ラッパー。"""

import pytesseract
from PIL import Image

from receipt_ocr.preprocessor import preprocess


def extract_text(image_path: str, lang: str = "jpn+eng") -> str:
    """画像ファイルからOCRテキストを抽出する。"""
    img = Image.open(image_path)
    processed = preprocess(img)
    text: str = pytesseract.image_to_string(processed, lang=lang)
    return text
