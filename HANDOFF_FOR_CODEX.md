# HANDOFF_FOR_CODEX

## 2026-05-26 Codex 作業メモ

対象: `receipt-ocr-tool`

### セットアップ診断CLIを追加

OCR本処理の前に、ローカル環境が動作条件を満たしているか確認できる `tools/check_setup.py` を追加しました。

確認内容:

- 主要ファイル構成
  - `main.py`
  - `requirements.txt`
  - `receipt_ocr/ocr.py`
  - `receipt_ocr/preprocessor.py`
  - `receipt_ocr/extractors/default.py`
  - `receipt_ocr/renamer.py`
  - `receipt_ocr/csv_writer.py`
- Python依存
  - `pytesseract`
  - `Pillow`
  - `opencv-python-headless`
- 外部OCR
  - `tesseract` 実行ファイル
  - Tesseract 日本語言語データ `jpn`
  - Tesseract 英語言語データ `eng`
- 任意バックエンド
  - `paddleocr` は未導入でも警告扱い

READMEにも `python tools/check_setup.py` の手順を追記済みです。

### 抽出ロジックの回帰テストを追加

`tests/test_default_extractor.py` を追加し、依存パッケージなしで `DefaultExtractor` の基本動作を確認できるようにしました。

確認内容:

- 西暦の日本語日付、合計金額、店舗名の抽出
- 令和日付の西暦変換
- 合計ラベルがない場合の最大金額採用

READMEのオプション表も、既存実装に合わせて `--engine` / `--list-engines` を追記しました。

### 検証

```powershell
& 'C:\Users\highd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile main.py receipt_ocr\ocr.py receipt_ocr\renamer.py receipt_ocr\csv_writer.py receipt_ocr\extractors\default.py tools\check_setup.py tests\test_default_extractor.py
& 'C:\Users\highd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests
& 'C:\Users\highd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\check_setup.py
```

この実行環境では `pytesseract`、`opencv-python-headless`、Tesseract本体が未導入でした。診断CLIは不足項目を `NG` として返す設計なので、ユーザー環境では `pip install -r requirements.txt` とTesseract日本語データ導入後に再実行してください。

### 次に着手しやすいこと

- `rename_file()` の重複時ファイル名生成を `name_1`, `name_2` 形式で安定化する
- 実画像の小さなfixtureを追加し、Tesseract導入済み環境でのスモークテストを整備する
- Windows向けにTesseractインストールパス設定例をREADMEへ追記する
