#!/usr/bin/env python3
"""Validate the local setup for receipt-ocr-tool.

The main OCR flow depends on both Python packages and the external Tesseract
binary. This doctor command reports missing pieces before users run a batch.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_MODULES = {
    "pytesseract": "pytesseract",
    "PIL": "Pillow",
    "cv2": "opencv-python-headless",
}

PROJECT_FILES = [
    "main.py",
    "requirements.txt",
    "receipt_ocr/ocr.py",
    "receipt_ocr/preprocessor.py",
    "receipt_ocr/extractors/default.py",
    "receipt_ocr/renamer.py",
    "receipt_ocr/csv_writer.py",
]


def _ok(message: str) -> None:
    print(f"OK   {message}")


def _warn(message: str) -> None:
    print(f"WARN {message}")


def _ng(message: str) -> None:
    print(f"NG   {message}")


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def check_project_files() -> list[str]:
    errors: list[str] = []
    for relative in PROJECT_FILES:
        path = ROOT / relative
        if path.exists():
            _ok(f"found {relative}")
        else:
            errors.append(f"missing required file: {relative}")
            _ng(errors[-1])
    return errors


def check_python_modules() -> list[str]:
    errors: list[str] = []
    for module_name, package_name in REQUIRED_MODULES.items():
        if _module_available(module_name):
            _ok(f"python package available: {package_name}")
        else:
            errors.append(
                f"missing Python package: {package_name} "
                f"(install with: python -m pip install -r requirements.txt)"
            )
            _ng(errors[-1])

    if _module_available("paddleocr"):
        _ok("optional package available: paddleocr")
    else:
        _warn("optional PaddleOCR backend is not installed")

    return errors


def _run_tesseract(args: list[str]) -> subprocess.CompletedProcess[str] | None:
    exe = shutil.which("tesseract")
    if exe is None:
        return None
    return subprocess.run(
        [exe, *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def check_tesseract() -> list[str]:
    errors: list[str] = []
    version_result = _run_tesseract(["--version"])
    if version_result is None:
        errors.append("tesseract executable not found on PATH")
        _ng(errors[-1])
        return errors

    first_line = (version_result.stdout or version_result.stderr).splitlines()[0]
    _ok(f"tesseract executable available: {first_line}")

    langs_result = _run_tesseract(["--list-langs"])
    if langs_result is None or langs_result.returncode != 0:
        errors.append("failed to list Tesseract languages")
        _ng(errors[-1])
        return errors

    langs = {
        line.strip()
        for line in langs_result.stdout.splitlines()
        if line.strip() and not line.lower().startswith("list of available")
    }
    if "jpn" in langs:
        _ok("Tesseract Japanese language data available: jpn")
    else:
        errors.append("Tesseract Japanese language data is missing: jpn")
        _ng(errors[-1])

    if "eng" in langs:
        _ok("Tesseract English language data available: eng")
    else:
        _warn("Tesseract English language data is missing: eng")

    return errors


def main() -> int:
    print(f"Checking receipt-ocr-tool setup under: {ROOT}")
    errors: list[str] = []
    errors.extend(check_project_files())
    errors.extend(check_python_modules())
    errors.extend(check_tesseract())

    if errors:
        print()
        print("Setup check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print()
    print("Receipt OCR setup check OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
