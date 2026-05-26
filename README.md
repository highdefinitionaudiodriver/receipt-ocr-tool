# Receipt OCR Renamer & CSV Aggregator

確定申告・医療費控除のためのローカル完結型レシート画像OCRツール。
クラウドAPIを一切使用せず、プライバシーを完全に保護します。

---

## 🎯 これは何？（30秒で）

- **誰のため**：医療費控除・経費精算でレシートを大量に管理する個人／個人事業主
- **何が解決される**：スマホで撮りためたレシート画像を **OCR で日付・金額・店舗名を自動抽出 → 規則的なファイル名にリネーム → CSV 集計**。年度末の入力作業を分単位に短縮
- **なぜ既存ツールではダメか**：家計簿アプリは月額課金＋クラウド送信が前提。本ツールは **完全ローカル（Tesseract）／API キー不要／プライバシー保護**
- **使う条件**：Python 3.10+ / Tesseract OCR（日本語データ）／Windows・macOS・Linux

## 💰 想定ユースケース・価格帯

| 用途 | 形態 |
|---|---|
| 個人の確定申告・医療費控除集計 | 無料（MIT） |
| 確定申告セット（Selfmed Tax + PDF 自動入力との組合せ） | 個別利用は無料、束ねたパッケージ販売は今後検討 |
| 個人事業主向け経費仕訳支援・カスタム抽出ルール開発 | 応相談 |

---

## 🎬 デモ

<!-- docs/demo.gif に「レシート画像フォルダを指定 → OCR → リネーム → summary.csv生成」までの30秒デモGIFを配置してください。 -->
![Receipt OCR demo](docs/demo.gif)

---

## 機能

- レシート画像（JPG/PNG）からOCRでテキストを抽出
- **OCR エンジン切替** — Tesseract (デフォルト) / **PaddleOCR** （日本語認識精度大幅向上）
- 正規表現で **日付**・**金額**・**店舗名** を自動認識
- ファイルを `YYYYMMDD_店舗名_金額円.jpg` に自動リネーム
- 集計用 CSV を自動生成
- 読み取り失敗ファイルは `needs_manual_check/` に自動分類

### OCR エンジン比較

| エンジン | 日本語認識精度 | 起動速度 | インストールサイズ | 推奨用途 |
|---|---|---|---|---|
| `tesseract` (デフォルト) | 標準 | 速い | 小 (~50MB) | 印字が綺麗な領収書、件数が多い |
| `paddle` | **大幅に高い** | 遅い (初回数秒) | 大 (~500MB+モデル) | 薄い印字、感熱紙、手書き混じり |

エンジン指定：

```bash
# Tesseract (デフォルト)
python main.py ./receipts

# PaddleOCR (要 pip install paddleocr paddlepaddle)
python main.py ./receipts --engine paddle

# 環境変数でも指定可
RECEIPT_OCR_ENGINE=paddle python main.py ./receipts

# 利用可能なエンジン一覧
python main.py --list-engines
```

## ディレクトリ構成

```
receipt-ocr-tool/
├── main.py                     # CLI エントリーポイント
├── requirements.txt
└── receipt_ocr/
    ├── ocr.py                  # Tesseract OCR ラッパー
    ├── preprocessor.py         # 画像前処理（グレースケール・二値化）
    ├── csv_writer.py           # CSV 出力
    ├── renamer.py              # リネーム・移動処理
    └── extractors/
        ├── base.py             # 抽出ルール基底クラス（ABC）
        └── default.py          # 汎用レシート抽出ルール
```

## 前提条件

- Python 3.10+
- Tesseract OCR（日本語言語データ含む）

### Tesseract のインストール

**Windows:**

[UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) からインストーラーをダウンロードし、インストール時に **Japanese** にチェックを入れてください。

**macOS:**

```bash
brew install tesseract tesseract-lang
```

**Ubuntu / Debian:**

```bash
sudo apt install tesseract-ocr tesseract-ocr-jpn
```

**インストール確認:**

```bash
tesseract --version
tesseract --list-langs   # "jpn" が含まれていれば OK
```

## セットアップ

```bash
git clone https://github.com/yourname/receipt-ocr-tool.git
cd receipt-ocr-tool
pip install -r requirements.txt
```

### セットアップ診断

OCR 実行前に Python パッケージ、Tesseract 本体、日本語言語データの状態を確認できます。

```bash
python tools/check_setup.py
```

## 使い方

```bash
# 基本実行
python main.py ./receipts

# CSV ファイル名を指定
python main.py ./receipts --output 医療費2025.csv

# 日本語のみで OCR
python main.py ./receipts --lang jpn

# リネーム・移動せず結果だけ確認（dry-run）
python main.py ./receipts --dry-run
```

### オプション一覧

| オプション | 短縮 | デフォルト | 説明 |
|---|---|---|---|
| `directory` | - | (必須) | レシート画像のディレクトリ |
| `--output` | `-o` | `summary.csv` | 出力CSVファイル名 |
| `--lang` | `-l` | `jpn+eng` | Tesseract言語設定 |
| `--engine` | `-e` | `tesseract` | OCRエンジン（`tesseract` / `paddle`） |
| `--list-engines` | - | `false` | 利用可能なOCRエンジンを表示して終了 |
| `--dry-run` | - | `false` | リネーム・移動を行わず結果を表示 |

## 処理フロー

```
画像読み込み
  ↓
画像前処理（グレースケール → ノイズ除去 → 適応的二値化）
  ↓
Tesseract OCR でテキスト抽出
  ↓
正規表現マッチング
  ├─ 日付: YYYY/MM/DD, YYYY年MM月DD日, 令和X年MM月DD日
  ├─ 金額: 合計行を優先、¥/円 表記に対応
  └─ 店舗名: 先頭行から推測
  ↓
┌─ 成功 → リネーム & CSV追記
└─ 失敗 → needs_manual_check/ へ移動
```

## 出力例

### リネーム結果

```
処理中: IMG_0012.jpg ... → 20250315_マツモトキヨシ_1280円.jpg
処理中: IMG_0013.jpg ... → 20250320_セブンイレブン_648円.jpg
処理中: IMG_0014.jpg ... 抽出失敗 → needs_manual_check

完了: 成功 2 件 / 要確認 1 件
CSV出力: ./receipts/summary.csv
```

### summary.csv

```csv
ファイル名,日付,店舗名,金額
20250315_マツモトキヨシ_1280円.jpg,2025/03/15,マツモトキヨシ,1280
20250320_セブンイレブン_648円.jpg,2025/03/20,セブンイレブン,648
```

## 抽出ルールの拡張

`BaseExtractor` を継承して専用の抽出ルールを追加できます。

```python
# receipt_ocr/extractors/pharmacy.py
from receipt_ocr.extractors.base import BaseExtractor, ReceiptData

class PharmacyExtractor(BaseExtractor):
    """薬局レシート専用の抽出ルール"""

    def extract(self, text: str) -> ReceiptData:
        # 薬局特有のフォーマットに対応した抽出ロジック
        ...
```

`main.py` で `extractor = PharmacyExtractor()` に差し替えるだけで利用できます。

## 注意事項

- OCR の精度はレシートの印字品質・撮影条件に依存します。`--dry-run` で事前確認を推奨します
- `needs_manual_check/` に分類されたファイルは手動で内容を確認してください
- すべての処理はローカルで完結します。ネットワーク通信は一切行いません

## ライセンス

MIT

---

## 🔗 確定申告セット（兄弟ツール）

本ツールは **3 兄弟ツール + ランチャー** の一部です。組み合わせで確定申告が一気通貫に：

```
[1] receipt-ocr-tool  ← このリポジトリ。レシート画像 → CSV
        ↓
[2] selfmed-tax-tool  ← 購入履歴 CSV → 対象医薬品 Excel
        ↓
[3] pdf-autofill-cli  ← 明細書 PDF 自動入力
        ↓
   税務署提出用 PDF 完成
```

- 🚀 **[tax-toolkit](https://github.com/highdefinitionaudiodriver/tax-toolkit)** — 上の 3 ステップを **1 つの GUI** で一気通貫実行（Tkinter ウィザード）
- 📦 [selfmed-tax-tool](https://github.com/highdefinitionaudiodriver/selfmed-tax-tool) — 通販購入履歴 CSV → セルフメディケーション税制対象品の Excel 出力
- 📝 [pdf-autofill-cli](https://github.com/highdefinitionaudiodriver/pdf-autofill-cli) — 医療費控除明細書 PDF 等への自動入力（座標指定 / フォームフィールド）

---

## 🤝 商用利用・カスタマイズ依頼

- 個人利用は無料（MIT ライセンス）
- 法人導入支援、カスタマイズ、業務テンプレ整備、追加機能開発は応相談
- 連絡先：highdefinitionaudiodriver@gmail.com

<!-- CODEX-CURRENT-STATUS:START -->
## 現状サマリ (2026-05-25)

- 対象: Receipt OCR Renamer & CSV Aggregator
- 作業ブランチ: main
- README更新時点の参照コミット: 2026-05-26 Codex作業時点
- Python 実行環境向けに requirements.txt を同梱。
- docs ディレクトリ配下に設計・運用・補足資料を配置。
- 主要な確認コマンド: `python tools/check_setup.py` / `python -m unittest discover -s tests`
- 次に進めるなら、重複ファイル名生成の安定化、実画像fixtureによるOCRスモークテスト、Windows向けTesseractパス設定例のREADME追記を行う。
<!-- CODEX-CURRENT-STATUS:END -->

