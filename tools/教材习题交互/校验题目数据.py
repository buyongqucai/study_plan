#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验题目 / 错题数据合法性。"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def load_js_assign(path: Path, name: str):
    text = path.read_text(encoding="utf-8").strip()
    m = re.search(rf"window\.{re.escape(name)}\s*=\s*", text)
    if not m:
        raise ValueError(f"找不到 window.{name}")
    payload = text[m.end() :].strip()
    if payload.endswith(";"):
        payload = payload[:-1].strip()
    return json.loads(payload)


def check_questions(questions: list, label: str) -> list[str]:
    errs: list[str] = []
    seen = set()
    for q in questions:
        qid = q.get("id")
        if qid in seen:
            errs.append(f"{label}: 题号重复 {qid}")
        seen.add(qid)
        opts = q.get("options") or {}
        for k in opts:
            if k not in "ABCDE":
                errs.append(f"{label} #{qid}: 非法选项键 {k}")
        ans = str(q.get("answer") or "")
        if not ans or any(c not in "ABCDE" for c in ans):
            errs.append(f"{label} #{qid}: 非法答案 {ans!r}")
        if not (q.get("stem") or "").strip():
            errs.append(f"{label} #{qid}: 空题干")
    return errs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--题目数据", help="题目数据.js")
    ap.add_argument("--错题数据", help="错题数据.js")
    args = ap.parse_args()
    errs: list[str] = []
    if args.题目数据:
        data = load_js_assign(Path(args.题目数据), "习题册章节")
        errs += check_questions(data.get("questions", []), "题目")
    if args.错题数据:
        data = load_js_assign(Path(args.错题数据), "错题本数据")
        errs += check_questions(data.get("questions", []), "错题")
    if errs:
        print("FAIL")
        for e in errs:
            print("-", e)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
