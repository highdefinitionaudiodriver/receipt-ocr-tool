---
title: "領収書 OCR ツール を作った — ローカル完結で動かす実用ツール"
emoji: "🛠️"
type: "tech"
topics: ["python", "個人開発", "oss"]
published: false
---

> 本記事は Zenn 用の下書きです。Qiita に出す場合は先頭の frontmatter を削除してください。

## TL;DR

確定申告・医療費控除のためのローカル完結型レシート画像OCRツール。 クラウドAPIを一切使用せず、プライバシーを完全に保護します。

- リポジトリ: https://github.com/highdefinitionaudiodriver/receipt-ocr-tool
- ライセンス: MIT / バージョン: v0.2.0

## 作った背景・課題

（なぜ作ったか。既存ツールの不満、手作業の手間などを 2〜3 段落で。）

## できること

- レシート画像（JPG/PNG）からOCRでテキストを抽出
- OCR エンジン切替 — Tesseract (デフォルト) / PaddleOCR （日本語認識精度大幅向上）
- 正規表現で 日付・金額・店舗名 を自動認識
- ファイルを YYYYMMDD_店舗名_金額円.jpg に自動リネーム
- 集計用 CSV を自動生成
- 読み取り失敗ファイルは needs_manual_check/ に自動分類

## 仕組み / 工夫した点

（設計上のポイント。ローカル完結・プライバシー配慮・依存の少なさ など。）

## 使い方

```bash
# インストール・起動例（README から転記）
```

## ハマったところ

（開発中の課題と解決。）

## おわりに

フィードバックは Issues / Star をいただけると励みになります。

リポジトリ: https://github.com/highdefinitionaudiodriver/receipt-ocr-tool
