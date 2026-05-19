"""汎用レシート抽出ルール。"""

import re
from typing import Optional

from receipt_ocr.extractors.base import BaseExtractor, ReceiptData


class DefaultExtractor(BaseExtractor):
    """一般的なレシートから日付・金額・店舗名を抽出する。"""

    # --- 日付パターン ---
    DATE_PATTERNS = [
        # 2024/03/15, 2024-03-15, 2024.03.15
        re.compile(r"(20\d{2})[/\-\.](0[1-9]|1[0-2])[/\-\.]([0-2]\d|3[01])"),
        # 2024年3月15日, 2024年03月15日
        re.compile(r"(20\d{2})\s*年\s*(0?[1-9]|1[0-2])\s*月\s*(0?[1-9]|[12]\d|3[01])\s*日"),
        # 令和6年3月15日 (令和元年=2019)
        re.compile(r"令和\s*(\d{1,2})\s*年\s*(0?[1-9]|1[0-2])\s*月\s*(0?[1-9]|[12]\d|3[01])\s*日"),
    ]

    # --- 金額パターン (合計行を優先) ---
    TOTAL_PATTERNS = [
        # 合計 ¥1,234 / 合計 1,234円 / 合計 1234
        re.compile(r"合\s*計[^\d￥¥]*[￥¥]?\s*([\d,]+)\s*円?"),
        # お買上合計, お会計
        re.compile(r"(?:お買[い上]?上?|お会計|税込|総[額計])[^\d￥¥]*[￥¥]?\s*([\d,]+)\s*円?"),
        # ¥1,234 or ￥1,234 (単独)
        re.compile(r"[￥¥]\s*([\d,]+)"),
        # 1,234円
        re.compile(r"([\d,]+)\s*円"),
    ]

    def extract(self, text: str) -> ReceiptData:
        date = self._extract_date(text)
        amount = self._extract_amount(text)
        store = self._extract_store(text)
        return ReceiptData(date=date, amount=amount, store=store)

    def _extract_date(self, text: str) -> Optional[str]:
        for pattern in self.DATE_PATTERNS:
            m = pattern.search(text)
            if m:
                groups = m.groups()
                if "令和" in pattern.pattern:
                    year = 2018 + int(groups[0])
                    month, day = int(groups[1]), int(groups[2])
                else:
                    year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                return f"{year:04d}{month:02d}{day:02d}"
        return None

    def _extract_amount(self, text: str) -> Optional[int]:
        candidates: list[int] = []
        for i, pattern in enumerate(self.TOTAL_PATTERNS):
            for m in pattern.finditer(text):
                raw = m.group(1).replace(",", "")
                if raw.isdigit():
                    val = int(raw)
                    if val > 0:
                        # 合計行パターン (index 0,1) は優先度高
                        if i <= 1:
                            return val
                        candidates.append(val)
        # 合計行が見つからなければ最大金額を採用
        return max(candidates) if candidates else None

    def _extract_store(self, text: str) -> Optional[str]:
        """先頭数行から店舗名らしき文字列を推測する。"""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for line in lines[:5]:
            # 日付・金額・記号のみの行はスキップ
            if re.fullmatch(r"[\d/\-\.\s年月日￥¥円,]+", line):
                continue
            # 電話番号行をスキップ
            if re.search(r"TEL|tel|電話|℡|\d{2,4}-\d{2,4}-\d{4}", line):
                continue
            # 短すぎる行 / レシートヘッダーの定型句をスキップ
            if len(line) < 2 or re.search(r"領収|レシート|明細", line):
                continue
            # 店舗名として採用 (ファイル名に使えない文字を除去)
            name = re.sub(r'[\\/:*?"<>|]', "", line)
            return name[:20]  # 長すぎる場合は切り詰め
        return None
