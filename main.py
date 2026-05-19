#!/usr/bin/env python3
"""
レシート画像 OCR リネーマー & CSV 集計 CLI ツール

Usage:
    python main.py ./receipts
    python main.py ./receipts --output result.csv --lang jpn
"""

import argparse
import sys
from pathlib import Path

from receipt_ocr.ocr import extract_text, available_engines
from receipt_ocr.extractors.default import DefaultExtractor
from receipt_ocr.renamer import build_new_name, rename_file, move_to_manual_check
from receipt_ocr.csv_writer import append_to_csv

SUPPORTED_EXT = {".jpg", ".jpeg", ".png"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="レシート画像を OCR → リネーム → CSV 集計するローカル専用ツール"
    )
    parser.add_argument(
        "directory", nargs="?", default=None,
        help="レシート画像が入ったディレクトリ（--list-engines 使用時は省略可）"
    )
    parser.add_argument(
        "--output", "-o", default="summary.csv", help="出力CSVファイル名 (default: summary.csv)"
    )
    parser.add_argument(
        "--lang", "-l", default="jpn+eng", help="Tesseract言語 (default: jpn+eng)"
    )
    parser.add_argument(
        "--engine", "-e", default=None, choices=["tesseract", "paddle"],
        help="OCR エンジン (default: tesseract / 環境変数 RECEIPT_OCR_ENGINE 上書き可)"
    )
    parser.add_argument(
        "--list-engines", action="store_true",
        help="利用可能な OCR エンジンを表示して終了"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="リネーム・移動せず結果だけ表示"
    )
    return parser.parse_args()


def collect_images(directory: Path) -> list[Path]:
    """対象ディレクトリから画像ファイル一覧を取得する。"""
    return sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXT
    )


def main() -> None:
    args = parse_args()

    if args.list_engines:
        engines = available_engines()
        print("利用可能な OCR エンジン:")
        for name, ok in engines.items():
            status = "[OK] 利用可能" if ok else "[--] 未インストール"
            print(f"  {name:10s} : {status}")
        print()
        print("PaddleOCR を使うには: pip install paddleocr paddlepaddle")
        sys.exit(0)

    if args.directory is None:
        print("エラー: ディレクトリを指定してください（--help / --list-engines も可）", file=sys.stderr)
        sys.exit(2)

    target_dir = Path(args.directory)

    if not target_dir.is_dir():
        print(f"エラー: ディレクトリが見つかりません: {target_dir}", file=sys.stderr)
        sys.exit(1)

    images = collect_images(target_dir)
    if not images:
        print("対象画像が見つかりませんでした。")
        sys.exit(0)

    csv_path = target_dir / args.output
    extractor = DefaultExtractor()

    success = 0
    failed = 0

    for img_path in images:
        print(f"処理中: {img_path.name} ... ", end="", flush=True)

        try:
            text = extract_text(str(img_path), lang=args.lang, engine=args.engine)
        except Exception as e:
            print(f"OCRエラー: {e}")
            if not args.dry_run:
                move_to_manual_check(img_path)
            failed += 1
            continue

        data = extractor.extract(text)

        # 日付と金額の両方が取れなければ手動確認送り
        if data.date is None and data.amount is None:
            print("抽出失敗 → needs_manual_check")
            if not args.dry_run:
                move_to_manual_check(img_path)
            failed += 1
            continue

        new_name = build_new_name(data, img_path)

        if args.dry_run:
            print(f"→ {new_name} (dry-run)")
        else:
            renamed = rename_file(img_path, new_name)
            append_to_csv(csv_path, renamed.name, data)
            print(f"→ {renamed.name}")

        success += 1

    print(f"\n完了: 成功 {success} 件 / 要確認 {failed} 件")
    if not args.dry_run and success > 0:
        print(f"CSV出力: {csv_path}")


if __name__ == "__main__":
    main()
