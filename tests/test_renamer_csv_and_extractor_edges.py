"""renamer / csv_writer の単体テストと DefaultExtractor の追加エッジケース."""
import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from receipt_ocr.csv_writer import append_to_csv, _format_date, HEADER
from receipt_ocr.extractors.base import ReceiptData
from receipt_ocr.extractors.default import DefaultExtractor
from receipt_ocr.renamer import build_new_name, rename_file, move_to_manual_check


class BuildNewNameTest(unittest.TestCase):
    def test_full_data(self):
        data = ReceiptData(date="20250315", amount=1280, store="マツキヨ")
        self.assertEqual(build_new_name(data, Path("a.JPG")), "20250315_マツキヨ_1280円.jpg")

    def test_missing_fields_use_placeholders(self):
        data = ReceiptData(date=None, amount=None, store=None)
        self.assertEqual(build_new_name(data, Path("x.png")), "nodate_不明_0円.png")


class RenameFileTest(unittest.TestCase):
    def test_rename_and_collision_counter(self):
        with TemporaryDirectory() as d:
            base = Path(d)
            (base / "a.txt").write_text("1", encoding="utf-8")
            first = rename_file(base / "a.txt", "out.txt")
            self.assertEqual(first.name, "out.txt")

            (base / "b.txt").write_text("2", encoding="utf-8")
            second = rename_file(base / "b.txt", "out.txt")
            # 衝突したので連番が付く
            self.assertEqual(second.name, "out_1.txt")

    def test_move_to_manual_check(self):
        with TemporaryDirectory() as d:
            base = Path(d)
            f = base / "blurry.jpg"
            f.write_text("x", encoding="utf-8")
            moved = move_to_manual_check(f)
            self.assertEqual(moved.parent.name, "needs_manual_check")
            self.assertFalse(f.exists())


class CsvWriterTest(unittest.TestCase):
    def test_creates_header_then_appends(self):
        with TemporaryDirectory() as d:
            csv_path = Path(d) / "summary.csv"
            append_to_csv(csv_path, "r1.jpg", ReceiptData(date="20250101", amount=500, store="店A"))
            append_to_csv(csv_path, "r2.jpg", ReceiptData(date=None, amount=None, store=None))

            with open(csv_path, encoding="utf-8-sig", newline="") as f:
                rows = list(csv.reader(f))
            self.assertEqual(rows[0], HEADER)
            self.assertEqual(rows[1], ["r1.jpg", "2025/01/01", "店A", "500"])
            # 欠損は空文字
            self.assertEqual(rows[2], ["r2.jpg", "", "", ""])

    def test_format_date(self):
        self.assertEqual(_format_date("20250315"), "2025/03/15")
        self.assertEqual(_format_date(None), "")
        self.assertEqual(_format_date("bad"), "bad")


class ExtractorEdgeCaseTest(unittest.TestCase):
    def setUp(self):
        self.ex = DefaultExtractor()

    def test_slash_dash_dot_date_formats(self):
        self.assertEqual(self.ex.extract("店\n2024/03/15\n¥500").date, "20240315")
        self.assertEqual(self.ex.extract("店\n2024-03-15\n¥500").date, "20240315")
        self.assertEqual(self.ex.extract("店\n2024.03.15\n¥500").date, "20240315")

    def test_total_takes_priority_over_standalone_yen(self):
        text = "店\n2024/03/15\n¥9999\n合計 1,200円"
        self.assertEqual(self.ex.extract(text).amount, 1200)

    def test_no_match_returns_none(self):
        data = self.ex.extract("---\n###\n")
        self.assertIsNone(data.date)
        self.assertIsNone(data.amount)

    def test_store_name_skips_phone_and_date_lines(self):
        text = "\n".join(["2024/03/15", "TEL 03-1234-5678", "ファミリーマート", "合計 300円"])
        self.assertEqual(self.ex.extract(text).store, "ファミリーマート")

    def test_store_name_strips_filename_unsafe_chars(self):
        text = "A/B:C*store\n2024/03/15\n¥100"
        store = self.ex.extract(text).store
        for ch in '\\/:*?"<>|':
            self.assertNotIn(ch, store)


if __name__ == "__main__":
    unittest.main()
