#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对目录内 PNG 做 RapidOCR，写出同名 .txt。"""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description="OCR 扫描页 PNG")
    ap.add_argument("--indir", required=True, help="含 PNG 的目录")
    ap.add_argument("--pattern", default="*.png")
    args = ap.parse_args()

    from rapidocr_onnxruntime import RapidOCR

    ocr = RapidOCR()
    indir = Path(args.indir)
    files = sorted(indir.glob(args.pattern))
    if not files:
        raise SystemExit(f"未找到 {args.pattern} 于 {indir}")

    for png in files:
        result, _ = ocr(str(png))
        lines = [item[1] for item in result] if result else []
        txt = png.with_suffix(".txt")
        txt.write_text("\n".join(lines), encoding="utf-8")
        print(png.name, "->", txt.name, f"({len(lines)} lines)")


if __name__ == "__main__":
    main()
