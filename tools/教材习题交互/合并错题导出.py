#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将浏览器导出错题 JSON 合并进 错题数据.js。"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_wrong_js(path: Path) -> dict:
    if not path.exists():
        return {"book": "", "subject": "", "questions": []}
    text = path.read_text(encoding="utf-8").strip()
    m = re.search(r"window\.错题本数据\s*=\s*", text)
    if not m:
        raise SystemExit(f"无法解析 {path}")
    payload = text[m.end() :].strip()
    if payload.endswith(";"):
        payload = payload[:-1].strip()
    return json.loads(payload)


def save_wrong_js(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "window.错题本数据 = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="合并导出错题到错题数据.js")
    ap.add_argument("--书目录", required=True, help="如 .../06-交互习题/必刷550")
    ap.add_argument("--导出", required=True, help="导出错题 JSON 路径")
    args = ap.parse_args()

    book_dir = Path(args.书目录)
    export_path = Path(args.导出)
    export = json.loads(export_path.read_text(encoding="utf-8"))
    target = book_dir / "错题数据.js"

    data = load_wrong_js(target)
    data["book"] = export.get("book") or data.get("book") or book_dir.name
    data["subject"] = export.get("subject") or data.get("subject") or ""
    by_id = {int(q["id"]): q for q in data.get("questions", [])}

    incoming = export.get("questions", [])
    for q in incoming:
        qid = int(q["id"])
        q = dict(q)
        q["fromSubmit"] = (
            f"做题本交卷 · {export.get('chapterId', '')} {export.get('chapterTitle', '')} · "
            f"{export.get('exportedAt', '')}"
        ).strip(" ·")
        by_id[qid] = q

    data["questions"] = [by_id[k] for k in sorted(by_id)]
    save_wrong_js(target, data)
    print(f"merged {len(incoming)} from export; total wrong = {len(data['questions'])}")
    print("wrote", target)


if __name__ == "__main__":
    main()
