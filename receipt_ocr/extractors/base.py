"""抽出ルールの基底クラス。

新しい抽出ルール（薬局専用など）を追加する場合は、
このクラスを継承して extract() メソッドを実装してください。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ReceiptData:
    """レシートから抽出されたデータ。"""

    date: Optional[str] = None  # YYYYMMDD 形式
    amount: Optional[int] = None  # 円単位の整数
    store: Optional[str] = None  # 店舗名


class BaseExtractor(ABC):
    """抽出ルールの基底クラス。"""

    @abstractmethod
    def extract(self, text: str) -> ReceiptData:
        """OCRテキストから日付・金額・店舗名を抽出する。"""
        ...
