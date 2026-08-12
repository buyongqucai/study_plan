#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按重复清单执行安全删除：同学段 + 类A + 体积阈值。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def top_segment(rel: str) -> str:
    return rel.split("/")[0] if rel else ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--list", required=True, help="重复文件清单.json")
    ap.add_argument("--record", required=True)
    ap.add_argument("--min-size", type=int, default=50_000)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    rows = json.loads(Path(args.list).read_text(encoding="utf-8"))
    deleted = []
    skipped = []

    for row in rows:
        if row.get("class") != "A":
            skipped.append((row["name"], "not A"))
            continue
        if row["size"] < args.min_size:
            skipped.append((row["name"], "too small"))
            continue
        paths = row["paths"]
        tops = {top_segment(p) for p in paths}
        if len(tops) != 1:
            skipped.append((row["name"], f"cross-top {tops}"))
            continue
        keep = row["keep"]
        keep_path = root / keep
        if not keep_path.exists():
            skipped.append((row["name"], "keep missing"))
            continue
        for p in paths:
            if p == keep:
                continue
            fp = root / p
            if not fp.exists():
                continue
            # extra safety: same size
            if fp.stat().st_size != row["size"]:
                skipped.append((p, "size mismatch"))
                continue
            deleted.append({"deleted": p, "kept": keep, "size": row["size"]})
            if args.apply:
                fp.unlink()

    record = Path(args.record)
    lines = [
        "# 去重执行记录",
        "",
        f"apply={args.apply}",
        f"删除数：{len(deleted)}",
        f"跳过组/项：{len(skipped)}",
        "",
        "## 已删除 / 将删除",
        "",
    ]
    for d in deleted[:1000]:
        lines.append(f"- 删 `{d['deleted']}` （保留 `{d['kept']}`，{d['size']} bytes）")
    lines.append("")
    lines.append("## 跳过摘要")
    from collections import Counter

    c = Counter(s for _, s in skipped)
    for k, v in c.most_common():
        lines.append(f"- {k}: {v}")
    record.write_text("\n".join(lines), encoding="utf-8")
    json_path = record.with_suffix(".json")
    json_path.write_text(
        json.dumps({"deleted": deleted, "skipped": skipped}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("deleted", len(deleted), "apply", args.apply)


if __name__ == "__main__":
    main()
