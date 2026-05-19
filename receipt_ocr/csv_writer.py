"""CSV 出力処理。"""

import csv
from pathlib import Path

from receipt_ocr.extractors.base import ReceiptData

HEADER = ["ファイル名", "日付", "店舗名", "金額"]


def append_to_csv(csv_path: Path, filename: str, data: ReceiptData) -> None:
    """summary.csv に1行追記する。ファイルが無ければヘッダー付きで新規作成。"""
    write_header = not csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(HEADER)
        writer.writerow([
            filename,
            _format_date(data.date),
            data.store or "",
            data.amount if data.amount is not None else "",
        ])


def _format_date(date_str: str | None) -> str:
    if date_str and len(date_str) == 8:
        return f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"
    return date_str or ""
