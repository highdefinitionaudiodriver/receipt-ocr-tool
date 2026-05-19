"""OCR精度向上のための画像前処理。"""

import cv2
import numpy as np
from PIL import Image


def preprocess(image: Image.Image) -> Image.Image:
    """グレースケール化 → ノイズ除去 → 二値化 を適用して返す。"""
    img = np.array(image)

    # グレースケール化
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img

    # 軽いノイズ除去
    denoised = cv2.medianBlur(gray, 3)

    # 適応的二値化 (影やムラに強い)
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 10
    )

    return Image.fromarray(binary)
