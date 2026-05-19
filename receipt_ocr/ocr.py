"""OCR エンジン抽象化レイヤ。

複数のバックエンド (Tesseract / PaddleOCR) を切り替え可能にする薄い
ファサード。`extract_text()` の API は後方互換を維持。

設計方針:
  - PaddleOCR は遅延 import（未インストール環境でも Tesseract のみで動作）
  - エンジン名は文字列 ("tesseract" / "paddle") で指定
  - PaddleOCR は日本語認識精度が Tesseract より大幅に高い一方、初回起動が
    重い (~数秒、モデルダウンロード時は十数秒)
"""

from __future__ import annotations

import os
from typing import Optional

from receipt_ocr.preprocessor import preprocess


# ──────────────────────────────────────────────────────────────────────────
# Tesseract バックエンド
# ──────────────────────────────────────────────────────────────────────────

def _extract_with_tesseract(image_path: str, lang: str = "jpn+eng") -> str:
    """Tesseract OCR で画像からテキストを抽出する。"""
    import pytesseract  # 遅延 import（pytesseract は軽量だが統一のため）
    from PIL import Image

    img = Image.open(image_path)
    processed = preprocess(img)
    text: str = pytesseract.image_to_string(processed, lang=lang)
    return text


# ──────────────────────────────────────────────────────────────────────────
# PaddleOCR バックエンド
# ──────────────────────────────────────────────────────────────────────────

# PaddleOCR インスタンスを使い回すためのモジュールレベルキャッシュ
_paddle_instance: Optional[object] = None


def _get_paddle_ocr(lang: str = "japan"):
    """PaddleOCR インスタンスを遅延生成・キャッシュする。

    PaddleOCR は内部でモデルをロードするため起動コストが高く、複数画像処理時は
    インスタンスを再利用する。

    Args:
        lang: PaddleOCR の言語コード。日本語は "japan"。
              （Tesseract 形式の "jpn+eng" 等が渡ってきた場合は "japan" に丸める）

    Returns:
        PaddleOCR インスタンス。
    """
    global _paddle_instance
    if _paddle_instance is not None:
        return _paddle_instance

    try:
        from paddleocr import PaddleOCR  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "PaddleOCR エンジンを使うには `pip install paddleocr paddlepaddle` "
            "（または GPU 版 `paddlepaddle-gpu`）が必要です。"
        ) from exc

    # Tesseract 言語コード ("jpn+eng" 等) は PaddleOCR の "japan" に丸める
    paddle_lang = "japan" if "jpn" in lang.lower() else "en"

    # use_angle_cls=True で 90°/180°/270° 回転したレシートにも対応
    _paddle_instance = PaddleOCR(use_angle_cls=True, lang=paddle_lang, show_log=False)
    return _paddle_instance


def _extract_with_paddle(image_path: str, lang: str = "japan") -> str:
    """PaddleOCR で画像からテキストを抽出する。

    日本語の認識率は Tesseract を大きく上回ることが多く、特に薄いレシート印字
    や手書きに近いフォントで効果が大きい。
    """
    ocr = _get_paddle_ocr(lang=lang)
    result = ocr.ocr(image_path, cls=True)

    if not result or not result[0]:
        return ""

    # PaddleOCR の戻り値: [[ [box], (text, confidence) ], ...]
    # 認識テキストを行単位で連結
    lines: list[str] = []
    for entry in result[0]:
        try:
            text = entry[1][0]
            if text:
                lines.append(text)
        except (IndexError, TypeError):
            continue
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────
# Public API（後方互換）
# ──────────────────────────────────────────────────────────────────────────

DEFAULT_ENGINE = os.environ.get("RECEIPT_OCR_ENGINE", "tesseract").lower()
VALID_ENGINES = {"tesseract", "paddle"}


def extract_text(image_path: str, lang: str = "jpn+eng", engine: Optional[str] = None) -> str:
    """画像ファイルから OCR でテキストを抽出する。

    Args:
        image_path: 画像ファイルのパス。
        lang: 言語指定。Tesseract 形式 ("jpn+eng" 等) を受け付ける。
              PaddleOCR では内部で "japan"/"en" に変換される。
        engine: バックエンド指定。`None` の場合は環境変数
                `RECEIPT_OCR_ENGINE` または "tesseract" を使用。

    Returns:
        OCR で抽出した生テキスト。

    Raises:
        ValueError: 未対応のエンジン名が指定された場合。
        RuntimeError: PaddleOCR エンジン選択時にパッケージ未インストール。
    """
    eng = (engine or DEFAULT_ENGINE).lower()
    if eng not in VALID_ENGINES:
        raise ValueError(
            f"未対応の OCR エンジン: {eng!r}。"
            f"使用可能: {sorted(VALID_ENGINES)}"
        )

    if eng == "paddle":
        return _extract_with_paddle(image_path, lang=lang)
    return _extract_with_tesseract(image_path, lang=lang)


def available_engines() -> dict[str, bool]:
    """各 OCR エンジンが現在の環境で利用可能かを返す。

    Returns:
        `{"tesseract": True, "paddle": False}` のような辞書。
    """
    status: dict[str, bool] = {}
    try:
        import pytesseract  # noqa: F401
        status["tesseract"] = True
    except ImportError:
        status["tesseract"] = False

    try:
        import paddleocr  # noqa: F401
        status["paddle"] = True
    except ImportError:
        status["paddle"] = False

    return status
