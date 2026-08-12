#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 PDF 指定页渲成 PNG。支持书页 + offset → PDF 页。"""
from __future__ import annotations

import argparse
from pathlib import Path

import fitz


def main() -> None:
    ap = argparse.ArgumentParser(description="渲染习题 PDF 页面为 PNG")
    ap.add_argument("--pdf", required=True, help="PDF 路径")
    ap.add_argument("--outdir", required=True, help="输出目录")
    ap.add_argument("--pdf-pages", help="PDF 页码（1-based），逗号或 起-止，如 8-12,147")
    ap.add_argument("--book-pages", help="书页码（1-based），需同时给 --offset")
    ap.add_argument("--offset", type=int, default=7, help="PDF页 = 书页 + offset（默认 7）")
    ap.add_argument("--zoom", type=float, default=2.2, help="渲染倍率")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    pdf = fitz.open(args.pdf)

    pages: list[int] = []
    if args.pdf_pages:
        pages.extend(parse_pages(args.pdf_pages))
    if args.book_pages:
        pages.extend(b + args.offset for b in parse_pages(args.book_pages))
    pages = sorted(set(pages))
    if not pages:
        raise SystemExit("请提供 --pdf-pages 或 --book-pages")

    mat = fitz.Matrix(args.zoom, args.zoom)
    for p in pages:
        if p < 1 or p > pdf.page_count:
            print(f"skip invalid page {p}")
            continue
        pix = pdf[p - 1].get_pixmap(matrix=mat)
        path = outdir / f"pdf页{p:03d}.png"
        pix.save(str(path))
        print("saved", path)


def parse_pages(spec: str) -> list[int]:
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


if __name__ == "__main__":
    main()
