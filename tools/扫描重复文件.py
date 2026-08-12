#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全库重复扫描：按 (文件名, 大小) 分组，输出清单。"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".cursor",
    "导出错题",
    "导出",
}
SKIP_SUFFIX = {".pyc", ".tmp"}


def iter_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        if p.suffix.lower() in SKIP_SUFFIX:
            continue
        try:
            rel = p.relative_to(root)
        except ValueError:
            continue
        yield p, rel, p.stat().st_size


def classify_group(paths: list[Path], root: Path) -> str:
    rels = [str(p.relative_to(root)).replace("\\", "/") for p in paths]
    brands = sum(1 for r in rels if "讲义-东奥" in r or "讲义-斯尔" in r or "讲义-正保" in r)
    # different brands same filename → B
    brand_set = set()
    for r in rels:
        for b in ("讲义-东奥", "讲义-斯尔", "讲义-正保"):
            if b in r:
                brand_set.add(b)
    if len(brand_set) >= 2:
        return "B"
    # note area holding materials
    if any("/02-章节笔记/" in r and (r.endswith(".pdf") or r.endswith(".docx")) for r in rels):
        return "C"
    # interactive duplicates 05 vs 06
    if any("05-错题本" in r for r in rels) and any("06-" in r for r in rels):
        return "A"
    # tools old/new
    if any("习题册交互" in r for r in rels) and any("教材习题交互" in r for r in rels):
        return "A"
    # same brand or same tree duplicates
    if brands >= 1 or len(paths) > 1:
        # prefer A for identical size+name duplicates under same brand or misc
        return "A" if len(brand_set) <= 1 else "B"
    return "A"


def prefer_keep(paths: list[Path], root: Path) -> Path:
    def score(p: Path) -> tuple:
        r = str(p.relative_to(root)).replace("\\", "/")
        s = 0
        if "/01-电子教材/" in r:
            s += 100
        if "/06-习题看板/" in r or "/06-交互习题/" in r:
            s += 80
        if "/tools/教材习题交互/" in r:
            s += 90
        if "/02-章节笔记/" in r:
            s -= 50
        if "/05-错题本/" in r and r.endswith((".html", ".js", ".css")):
            s -= 30
        if "习题册交互" in r:
            s -= 20
        # shorter path slight preference
        s -= r.count("/")
        return (s, -len(r))

    return max(paths, key=score)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-size", type=int, default=1)
    args = ap.parse_args()
    root = Path(args.root)
    groups: dict[tuple[str, int], list[Path]] = defaultdict(list)
    for p, rel, size in iter_files(root):
        if size < args.min_size:
            continue
        groups[(p.name.lower(), size)].append(p)

    dups = {k: v for k, v in groups.items() if len(v) > 1}
    rows = []
    for (name, size), paths in sorted(dups.items(), key=lambda x: -x[0][1]):
        cls = classify_group(paths, root)
        keep = prefer_keep(paths, root)
        rows.append(
            {
                "name": name,
                "size": size,
                "class": cls,
                "keep": str(keep.relative_to(root)).replace("\\", "/"),
                "paths": [str(p.relative_to(root)).replace("\\", "/") for p in paths],
            }
        )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 重复文件清单（全库扫描）",
        "",
        f"根目录：`{root}`",
        f"重复组数：{len(rows)}",
        "",
        "分类：A=可去重副本；B=多品牌故意并存（不删）；C=错放。",
        "",
    ]
    for i, row in enumerate(rows[:500], 1):
        lines.append(f"## {i}. `{row['name']}` ({row['size']} bytes) · 类 {row['class']}")
        lines.append(f"- 建议保留：`{row['keep']}`")
        for p in row["paths"]:
            mark = " ← keep" if p == row["keep"] else ""
            lines.append(f"- `{p}`{mark}")
        lines.append("")
    if len(rows) > 500:
        lines.append(f"… 另有 {len(rows) - 500} 组省略，见 JSON。")
    out.write_text("\n".join(lines), encoding="utf-8")
    json_path = out.with_suffix(".json")
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print("groups", len(rows), "wrote", out)


if __name__ == "__main__":
    main()
