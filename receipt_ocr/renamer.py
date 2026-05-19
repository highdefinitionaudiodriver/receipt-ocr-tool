"""ファイルリネーム・移動処理。"""

import shutil
from pathlib import Path

from receipt_ocr.extractors.base import ReceiptData

MANUAL_CHECK_DIR = "needs_manual_check"


def build_new_name(data: ReceiptData, original: Path) -> str:
    """ReceiptData からリネーム後のファイル名を生成する。"""
    date_part = data.date or "nodate"
    store_part = data.store or "不明"
    amount_part = f"{data.amount}円" if data.amount is not None else "0円"
    suffix = original.suffix.lower()
    return f"{date_part}_{store_part}_{amount_part}{suffix}"


def rename_file(original: Path, new_name: str) -> Path:
    """ファイルをリネームする。同名ファイルがあれば連番を付与。"""
    dest = original.parent / new_name
    counter = 1
    while dest.exists():
        stem = dest.stem
        dest = original.parent / f"{stem}_{counter}{dest.suffix}"
        counter += 1
    return original.rename(dest)


def move_to_manual_check(original: Path) -> Path:
    """OCR 抽出失敗ファイルを needs_manual_check へ移動する。"""
    check_dir = original.parent / MANUAL_CHECK_DIR
    check_dir.mkdir(exist_ok=True)
    dest = check_dir / original.name
    counter = 1
    while dest.exists():
        dest = check_dir / f"{original.stem}_{counter}{original.suffix}"
        counter += 1
    return Path(shutil.move(str(original), str(dest)))
