# -*- coding: utf-8 -*-
"""校验简历：YAML 结构、PDF 页数与分页、关键词覆盖。有错误时退出码非 0。"""
import argparse
import sys
import unicodedata
from pathlib import Path

import yaml


def norm(text: str) -> str:
    """把部首码位（部分字体导出 PDF 时的替代编码）还原成普通汉字，其余字符保持原样。"""
    out = []
    for ch in text:
        if 0x2E80 <= ord(ch) <= 0x2FDF:
            out.append(unicodedata.normalize("NFKC", ch))
        else:
            out.append(ch)
    return "".join(out)


def load_yaml(root: Path):
    path = root / "resume.yml"
    if not path.exists():
        raise SystemExit(f"未找到 {path}，请先运行 init.py 初始化")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}, path


def check_data(data: dict):
    """结构校验，返回 (errors, warnings)"""
    errs, warns = [], []

    for key in ("name", "intent", "summary"):
        if not str(data.get(key, "")).strip():
            errs.append(f"缺少字段或为空：{key}")
    for key in ("meta", "contact"):
        if not data.get(key):
            errs.append(f"缺少或为空的列表：{key}")

    comps = data.get("competencies") or []
    if len(comps) < 3:
        warns.append(f"核心能力只有 {len(comps)} 条，建议 4–6 条")
    for i, c in enumerate(comps, 1):
        if not str(c.get("label", "")).strip() or not str(c.get("text", "")).strip():
            errs.append(f"core competencies 第 {i} 条缺少 label 或 text")

    jobs = data.get("experience") or []
    if not jobs:
        errs.append("experience 至少需要一段经历")
    for i, e in enumerate(jobs, 1):
        for key in ("company", "date", "role", "industry"):
            if not str(e.get(key, "")).strip():
                errs.append(f"experience 第 {i} 段缺少 {key}")
        bullets = e.get("bullets") or []
        if not bullets:
            errs.append(f"experience 第 {i} 段没有 bullets")
        for j, b in enumerate(bullets, 1):
            if not str(b.get("label", "")).strip() or not str(b.get("text", "")).strip():
                errs.append(f"experience 第 {i} 段第 {j} 条 bullet 缺少 label 或 text")

    edus = data.get("education") or []
    if not edus:
        errs.append("education 至少需要一条")
    for i, e in enumerate(edus, 1):
        for key in ("school", "date", "major", "degree"):
            if not str(e.get(key, "")).strip():
                errs.append(f"education 第 {i} 条缺少 {key}")

    if not data.get("certificates"):
        warns.append("certificates 为空，若无证书可删掉该字段")

    text = yaml.safe_dump(data, allow_unicode=True)
    if "【待填】" in norm(text):
        warns.append("仍存在【待填】占位，投递前需替换为真实信息")
    return errs, warns


def find_pdf(root: Path, given: str | None):
    if given:
        p = Path(given).resolve()
        return p if p.exists() else None
    pdfs = sorted(root.glob("个人简历-*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pdfs[0] if pdfs else None


def check_pdf(pdf: Path, expect_pages: int):
    """页数、空页、每页首尾行，返回 (errors, warnings, page_lines)"""
    from pypdf import PdfReader

    errs, warns, lines = [], [], []
    reader = PdfReader(str(pdf))
    n = len(reader.pages)
    if expect_pages and n != expect_pages:
        errs.append(f"页数为 {n}，期望 {expect_pages}")

    for i, page in enumerate(reader.pages, 1):
        text = norm(page.extract_text() or "").strip()
        rows = [r.strip() for r in text.splitlines() if r.strip()]
        if not rows:
            errs.append(f"第 {i} 页没有提取到文字")
            lines.append((i, "", ""))
            continue
        lines.append((i, rows[0], rows[-1]))
        if i > 1 and rows[0] in ("自我概述", "SUMMARY"):
            warns.append(f"第 {i} 页从章节标题开始，上一页尾部可能过空")
    return errs, warns, lines


def check_keywords(data: dict, keywords: list[str]):
    """关键词覆盖：比对 resume.yml 内容（PDF 文字提取会受字体编码影响）"""
    if not keywords:
        return []
    text = norm(yaml.safe_dump(data, allow_unicode=True))
    missing = [k for k in keywords if norm(k) not in text]
    return ["内容中未找到关键词：" + "、".join(missing)] if missing else []


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="校验简历内容与 PDF")
    ap.add_argument("--root", default=".", help="简历内容目录")
    ap.add_argument("--pdf", help="指定 PDF；默认取目录中最新的 个人简历-*.pdf")
    ap.add_argument("--pages", type=int, default=2, help="期望页数，0 表示不校验")
    ap.add_argument("--keywords", default="", help="逗号分隔的 JD 关键词，校验是否出现在简历内容中")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    data, _ = load_yaml(root)
    errs, warns = check_data(data)

    kws = [k.strip() for k in a.keywords.replace("，", ",").split(",") if k.strip()]
    errs += check_keywords(data, kws)

    pdf = find_pdf(root, a.pdf)
    if pdf:
        pdf_errs, pdf_warns, lines = check_pdf(pdf, a.pages)
        errs += pdf_errs
        warns += pdf_warns
    else:
        lines = []
        warns.append("未找到 PDF，跳过页数/分页校验（先运行 build.py pdf）")

    print(f"内容目录：{root}")
    if pdf:
        print(f"PDF：{pdf.name}")
        for i, first, last in lines:
            print(f"  第 {i} 页  首：{first[:40]}  尾：{last[:40]}")
    for w in warns:
        print("WARN", w)
    for e in errs:
        print("FAIL", e)
    print("结果：", "PASS" if not errs else f"FAIL（{len(errs)} 项错误，{len(warns)} 项提醒）")
    raise SystemExit(0 if not errs else 1)


if __name__ == "__main__":
    main()
