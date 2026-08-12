# -*- coding: utf-8 -*-
"""将【讲义】源目录按科目/品牌复制到进阶计划。"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

DEFAULT_SRC = Path(r"D:\浏览器下载文件\【讲义】")
DEFAULT_DST = Path(__file__).resolve().parents[1]


def copy_tree(src: Path, dst: Path, force: bool) -> None:
    if not src.exists():
        print(f"SKIP missing: {src}")
        return
    dst.mkdir(parents=True, exist_ok=True)
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not force:
            if target.stat().st_size == path.stat().st_size:
                continue
        shutil.copy2(path, target)
    print(f"OK  {src}")
    print(f" -> {dst}")


def match_subject(folder: str, rules: list[tuple[str, str]]) -> str | None:
    for keyword, subject in rules:
        if keyword in folder:
            return subject
    return None


def sync_group(
    src_root: Path,
    dst_root: Path,
    exam_folder: str,
    brand_map: dict[str, str],
    rules: list[tuple[str, str]],
    dest_exam: str,
    force: bool,
) -> None:
    exam_src = src_root / exam_folder
    if not exam_src.exists():
        print(f"SKIP exam: {exam_src}")
        return
    for brand_dir, brand_name in brand_map.items():
        brand_src = exam_src / brand_dir
        if not brand_src.is_dir():
            continue
        for child in sorted(brand_src.iterdir()):
            if not child.is_dir():
                continue
            subject = match_subject(child.name, rules)
            if not subject:
                print(f"WARN unrecognized: {child}")
                continue
            dest = dst_root / dest_exam / subject / "01-电子教材" / brand_name / child.name
            copy_tree(child, dest, force)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC)
    parser.add_argument("--dst", type=Path, default=DEFAULT_DST)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not args.src.exists():
        print(f"源目录不存在: {args.src}", file=sys.stderr)
        return 1
    if not args.dst.exists():
        print(f"目标目录不存在: {args.dst}", file=sys.stderr)
        return 1

    tax_rules = [
        ("税一", "税法一"),
        ("税二", "税法二"),
        ("实务", "涉税服务实务"),
        ("法律", "涉税服务相关法律"),
        ("财会", "财务与会计"),
    ]
    cpa_rules = [
        ("综合", "综合阶段"),
        ("战略", "公司战略与风险管理"),
        ("财管", "财务成本管理"),
        ("经济法", "经济法"),
        ("税法", "税法"),
        ("审计", "审计"),
        ("会计", "会计"),
    ]
    zj_rules = [
        ("实务", "中级会计实务"),
        ("经济法", "经济法"),
        ("经济", "经济法"),
        ("财管", "财务管理"),
    ]

    sync_group(
        args.src,
        args.dst,
        "税务师",
        {
            "税务师-东奥": "讲义-东奥",
            "税务师-斯尔": "讲义-斯尔",
            "税务师-正保": "讲义-正保",
        },
        tax_rules,
        "01-税务师",
        args.force,
    )
    sync_group(
        args.src,
        args.dst,
        "注会",
        {
            "注会-东奥": "讲义-东奥",
            "注会-斯尔": "讲义-斯尔",
            "注会-正保": "讲义-正保",
        },
        cpa_rules,
        "02-CPA",
        args.force,
    )
    sync_group(
        args.src,
        args.dst,
        "中级",
        {
            "中级-东奥": "讲义-东奥",
            "中级-斯尔": "讲义-斯尔",
            "中级-正保": "讲义-正保",
        },
        zj_rules,
        "04-中级",
        args.force,
    )
    print("完成。抽查 税法一 / 会计 / 04-中级 下的 讲义-* 目录。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
