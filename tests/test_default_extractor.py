import unittest

from receipt_ocr.extractors.default import DefaultExtractor


class DefaultExtractorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = DefaultExtractor()

    def test_extracts_japanese_date_total_and_store(self) -> None:
        text = "\n".join([
            "マツモトキヨシ",
            "2025年3月15日",
            "小計 1,000円",
            "合計 1,280円",
        ])

        data = self.extractor.extract(text)

        self.assertEqual(data.date, "20250315")
        self.assertEqual(data.amount, 1280)
        self.assertEqual(data.store, "マツモトキヨシ")

    def test_extracts_reiwa_date(self) -> None:
        data = self.extractor.extract("サンプル薬局\n令和6年12月1日\nお会計 980円")

        self.assertEqual(data.date, "20241201")
        self.assertEqual(data.amount, 980)
        self.assertEqual(data.store, "サンプル薬局")

    def test_uses_largest_amount_when_total_label_is_missing(self) -> None:
        data = self.extractor.extract("ドラッグストア\n2025/01/02\n120円\n1,234円")

        self.assertEqual(data.date, "20250102")
        self.assertEqual(data.amount, 1234)


if __name__ == "__main__":
    unittest.main()
