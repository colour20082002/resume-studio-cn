# -*- coding: utf-8 -*-
"""初始化简历工程目录：复制起始 resume.yml，不覆盖已有文件。"""
import argparse
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STARTER = SCRIPT_DIR.parent / "assets" / "starter"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="初始化简历内容目录")
    ap.add_argument("--root", default=".", help="目标目录，默认当前目录")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的 resume.yml")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    target = root / "resume.yml"
    if target.exists() and not a.force:
        raise SystemExit(f"{target} 已存在，未覆盖（如需覆盖加 --force）")
    shutil.copy2(STARTER / "resume.yml", target)

    print(f"已初始化：{target}")
    print(f"下一步：编辑 resume.yml，然后运行 build.py --root \"{root}\"")


if __name__ == "__main__":
    main()
