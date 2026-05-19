# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- README に「これは何？（30秒で）」「想定ユースケース・価格帯」セクションを追加
- SECURITY.md を追加（脆弱性報告フロー）
- 商用利用・カスタマイズ依頼の連絡先を README 末尾に明記
- **PaddleOCR バックエンドのオプション対応**
  - `receipt_ocr/ocr.py` を OCR エンジン抽象化レイヤに刷新
  - Tesseract (デフォルト) / PaddleOCR を `--engine` フラグまたは環境変数で切替
  - `--list-engines` で利用可能なエンジンを表示
  - PaddleOCR インスタンスは遅延 import + キャッシュで複数画像処理時の起動コスト削減
  - `extract_text()` の既存 API は後方互換維持
  - PaddleOCR は requirements.txt にコメントで追加（必須ではなくオプション扱い）

## [0.1.0]

### Added
- 初版リリース
