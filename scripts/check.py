# -*- coding: utf-8 -*-
"""校验简历：YAML 结构、PDF 页数与分页、关键词覆盖。有错误时退出码非 0。"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

import yaml

WEAK_STARTS = ("负责", "协助", "参与", "配合", "帮助")
EMPTY_PHRASES = ("认真负责", "吃苦耐劳", "学习能力强", "抗压能力强", "沟通能力强",
                 "团队合作", "责任心强", "执行力强", "精通", "熟练掌握")
DATE_RE = re.compile(r"^(\d{4})\.(\d{2})\s*[–\-]\s*(?:(\d{4})\.(\d{2})|至今)$")
CJK_LATIN_RE = re.compile(r"[\u4e00-\u9fff][A-Za-z0-9]|[A-Za-z0-9][\u4e00-\u9fff]")


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

    show_cert = (data.get("sections") or {}).get("certificates", True) is not False
    if show_cert and not data.get("certificates"):
        warns.append("certificates 为空，若无证书可删掉该字段")

    text = yaml.safe_dump(data, allow_unicode=True)
    if "【待填】" in norm(text):
        warns.append("仍存在【待填】占位，投递前需替换为真实信息")
    return errs, warns


def check_style(data: dict):
    """内容体检：量化、动词、空话、日期、命名等，只提示不拦截。"""
    warns = []
    sections = data.get("sections") or {}
    shown = lambda key: sections.get(key, True) is not False

    summary = str(data.get("summary", "")).strip()
    if shown("summary") and summary:
        if len(summary) > 140:
            warns.append(f"自我概述 {len(summary)} 字，建议压缩到 80–140 字")
        elif len(summary) < 80:
            warns.append(f"自我概述仅 {len(summary)} 字，建议补充到 80–140 字")

    jobs = data.get("experience") or [] if shown("experience") else []
    bullets = [str(b.get("text", "")).strip()
               for e in jobs for b in (e.get("bullets") or [])]

    if bullets:
        quantified = [t for t in bullets if re.search(r"\d", t)]
        if len(quantified) / len(bullets) < 0.5:
            warns.append(f"量化不足：{len(bullets)} 条中仅 {len(quantified)} 条含数字，建议 ≥50%")
        weak = [t for t in bullets if t.startswith(WEAK_STARTS)]
        if weak:
            warns.append(f"{len(weak)} 条以弱势动词开头（负责/协助/参与），例：{weak[0][:20]}")
        long_ones = [t for t in bullets if len(t) > 50]
        if long_ones:
            warns.append(f"{len(long_ones)} 条超过 50 字，例：{long_ones[0][:20]}…")
        if any("我" in t for t in bullets):
            warns.append("条目中出现第一人称「我」")
        hits = [p for p in EMPTY_PHRASES if p in summary or any(p in t for t in bullets)]
        if hits:
            warns.append("空话或无证据词：" + "、".join(hits) + "（需跟事实或删掉）")
        tight = [t for t in bullets if CJK_LATIN_RE.search(t)]
        if tight:
            warns.append(f"{len(tight)} 条中英文/数字之间缺半角空格，例：{tight[0][:20]}")

    labels = [str(b.get("label", "")).strip()
              for e in jobs for b in (e.get("bullets") or [])]
    dups = sorted({x for x in labels if x and labels.count(x) > 1})
    if dups:
        warns.append("bullet 标签重复：" + "、".join(dups))

    prev_start = prev_end = None
    for i, e in enumerate(jobs, 1):
        date = str(e.get("date", "")).strip()
        m = DATE_RE.match(date)
        if not m:
            warns.append(f"第 {i} 段日期格式不规范：{date}（应为 YYYY.MM – YYYY.MM）")
            continue
        start = (int(m.group(1)), int(m.group(2)))
        end = (int(m.group(3)), int(m.group(4))) if m.group(3) else (9999, 12)
        if prev_end and end > prev_end:
            warns.append(f"经历未按时间倒序：第 {i} 段「{date}」晚于上一段")
        elif prev_start and m.group(3) and end > prev_start:
            warns.append(f"时间区间重叠：第 {i} 段「{date}」与上一段交叉")
        prev_start, prev_end = start, end

    contact = " ".join(str(x) for x in (data.get("contact") or []))
    if shown("contact") and re.search(r"@(qq|163|126)\.com", contact, re.I):
        warns.append("联系邮箱为个人邮箱，建议改用商务/专业邮箱")
    return warns


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
    ap.add_argument("--pages", type=int, default=None,
                    help="期望页数；默认读 resume.yml 的 pages（缺省 1），0 表示不校验")
    ap.add_argument("--keywords", default="", help="逗号分隔的 JD 关键词，校验是否出现在简历内容中")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    data, _ = load_yaml(root)
    errs, warns = check_data(data)
    warns += check_style(data)
    pages = a.pages if a.pages is not None else int(data.get("pages", 1) or 0)

    kws = [k.strip() for k in a.keywords.replace("，", ",").split(",") if k.strip()]
    errs += check_keywords(data, kws)

    pdf = find_pdf(root, a.pdf)
    if pdf:
        pdf_errs, pdf_warns, lines = check_pdf(pdf, pages)
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
