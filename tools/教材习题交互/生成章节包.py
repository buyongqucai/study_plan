#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从章节 JSON 生成 题目数据.js 与 做题本.html。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


TEMPLATE_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>做题本 · {book} · {chapter_title}</title>
  <link rel="stylesheet" href="../共用资源/共用样式.css" />
</head>
<body>
  <main class="page" id="appRoot"
    data-book="{book}"
    data-subject="{subject}"
    data-chapter-id="{chapter_id}"
    data-chapter-title="{chapter_title}"
    data-wrongbook-href="../错题本.html">
  </main>
  <script src="./题目数据.js"></script>
  <script src="../共用资源/做题逻辑.js"></script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="生成章节做题包")
    ap.add_argument("--json", required=True, help="章节结构化 JSON 路径")
    ap.add_argument("--outdir", required=True, help="输出章目录，如 .../第01章-税法基本原理")
    args = ap.parse_args()

    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    book = data.get("book", "必刷550")
    subject = data.get("subject", "税法一")
    chapter_id = data.get("chapterId", "第01章")
    chapter_title = data.get("chapterTitle", "")
    questions = data.get("questions", [])

    js = (
        "window.习题册章节 = "
        + json.dumps(
            {
                "book": book,
                "subject": subject,
                "chapterId": chapter_id,
                "chapterTitle": chapter_title,
                "questions": questions,
            },
            ensure_ascii=False,
            indent=2,
        )
        + ";\n"
    )
    (outdir / "题目数据.js").write_text(js, encoding="utf-8")

    html = TEMPLATE_HTML.format(
        book=book,
        subject=subject,
        chapter_id=chapter_id,
        chapter_title=chapter_title,
    )
    (outdir / "做题本.html").write_text(html, encoding="utf-8")
    print("wrote", outdir / "题目数据.js")
    print("wrote", outdir / "做题本.html", f"({len(questions)} 题)")


if __name__ == "__main__":
    main()
