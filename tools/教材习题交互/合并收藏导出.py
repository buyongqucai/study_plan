#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将收藏导出 JSON 合并进 收藏数据.js。"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_js(path: Path, name: str) -> dict:
    if not path.exists():
        return {"book": "", "subject": "", "questions": []}
    text = path.read_text(encoding="utf-8").strip()
    m = re.search(rf"window\.{re.escape(name)}\s*=\s*", text)
    if not m:
        raise SystemExit(f"无法解析 {path}")
    payload = text[m.end() :].strip()
    if payload.endswith(";"):
        payload = payload[:-1].strip()
    return json.loads(payload)


def save_js(path: Path, name: str, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"window.{name} = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--书目录", required=True)
    ap.add_argument("--导出", required=True)
    args = ap.parse_args()
    book_dir = Path(args.书目录)
    export = json.loads(Path(args.导出).read_text(encoding="utf-8"))
    target = book_dir / "收藏数据.js"
    data = load_js(target, "收藏题本数据")
    data["book"] = export.get("book") or data.get("book") or book_dir.name
    data["subject"] = export.get("subject") or data.get("subject") or ""
    by_id = {int(q["id"]): q for q in data.get("questions", [])}
    for q in export.get("questions", []):
        qid = int(q["id"])
        q = dict(q)
        q["fromSubmit"] = (
            f"收藏 · {export.get('chapterId', '')} {export.get('chapterTitle', '')} · "
            f"{export.get('exportedAt', '')}"
        ).strip(" ·")
        by_id[qid] = q
    data["questions"] = [by_id[k] for k in sorted(by_id)]
    save_js(target, "收藏题本数据", data)
    print(f"favorites total={len(data['questions'])} wrote {target}")


if __name__ == "__main__":
    main()
