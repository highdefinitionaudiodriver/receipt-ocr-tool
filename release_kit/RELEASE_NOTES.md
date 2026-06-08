# 領収書 OCR ツール v0.2.0

確定申告・医療費控除のためのローカル完結型レシート画像OCRツール。 クラウドAPIを一切使用せず、プライバシーを完全に保護します。

## 主な機能

- レシート画像（JPG/PNG）からOCRでテキストを抽出
- OCR エンジン切替 — Tesseract (デフォルト) / PaddleOCR （日本語認識精度大幅向上）
- 正規表現で 日付・金額・店舗名 を自動認識
- ファイルを YYYYMMDD_店舗名_金額円.jpg に自動リネーム
- 集計用 CSV を自動生成
- 読み取り失敗ファイルは needs_manual_check/ に自動分類

## 動作環境

- Windows 10/11, macOS 12+, Linux / Python 3.10 以上

## ダウンロード

- `*.zip` … 実行ファイル一式（解凍してそのまま実行）
- ソースコードは下記リポジトリを参照

## ライセンス / 連絡先

- MIT License
- https://github.com/highdefinitionaudiodriver/receipt-ocr-tool
- highdefinitionaudiodriver@gmail.com

## 変更履歴

（`CHANGELOG.md` の該当バージョンを転記してください）
