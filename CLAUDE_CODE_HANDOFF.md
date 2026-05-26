# CLAUDE_CODE_HANDOFF

## 2026-05-26

Codexが `receipt-ocr-tool` にセットアップ診断CLIを追加しました。

- 追加: `tools/check_setup.py`
- 追加: `tests/test_default_extractor.py`
- 更新: `README.md`
- 追加: `HANDOFF_FOR_CODEX.md`

診断CLIは、Python依存、Tesseract実行ファイル、日本語言語データ、主要ファイル構成を確認します。PaddleOCRは任意バックエンドなので未導入でも警告扱いです。

`DefaultExtractor` のunittestも追加し、西暦日付、令和日付、最大金額採用の基本パスを固定化しました。READMEのオプション表には既存実装に合わせて `--engine` / `--list-engines` を追記しています。

検証:

```powershell
python -m py_compile main.py receipt_ocr\ocr.py receipt_ocr\renamer.py receipt_ocr\csv_writer.py receipt_ocr\extractors\default.py tools\check_setup.py tests\test_default_extractor.py
python -m unittest discover -s tests
python tools\check_setup.py
```

この実行環境では `pytesseract`、`opencv-python-headless`、Tesseract本体が未導入のため、診断CLIは期待どおり `NG` を返しました。

次に進めるなら、重複ファイル名生成の安定化、実画像fixtureによるOCRスモークテスト、Windows向けTesseractパス設定例のREADME追記が着手しやすいです。
