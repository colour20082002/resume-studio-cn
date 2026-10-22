# -*- coding: utf-8 -*-
"""简历可视化编辑器：本地网页表单编辑 resume.yml，实时预览并导出当前组合。"""
import argparse
import io
import json
import shutil
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yaml
from PIL import Image, ImageOps

import build

SCRIPT_DIR = Path(__file__).resolve().parent     # 编辑器与模板资源
ROOT = Path.cwd()                                # 简历内容目录
YML = ROOT / "resume.yml"
BAK = ROOT / "resume.yml.bak"
EDITOR = SCRIPT_DIR / "editor.html"

DEFAULT_LAYOUT, DEFAULT_PALETTE, DEFAULT_FONT = build.MATCHES[0]

_lock = threading.Lock()


def dump_yaml(data: dict) -> str:
    def rep(dumper, text):
        style = "|" if "\n" in text else None
        return dumper.represent_scalar("tag:yaml.org,2002:str", text, style=style)

    class Dumper(yaml.SafeDumper):
        pass

    Dumper.add_representer(str, rep)
    return yaml.dump(data, Dumper=Dumper, allow_unicode=True,
                     sort_keys=False, default_flow_style=False, width=100000)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # 静默访问日志
        pass

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in ("/", "/index.html"):
            self._send(200, EDITOR.read_bytes(), "text/html; charset=utf-8")
        elif url.path == "/api/data":
            data = yaml.safe_load(YML.read_text(encoding="utf-8"))
            self._send(200, json.dumps(data, ensure_ascii=False).encode(),
                       "application/json; charset=utf-8")
        elif url.path == "/api/themes":
            body = {
                "layouts": [{"key": k, "label": v[0]} for k, v in build.LAYOUTS.items()],
                "palettes": [{"key": k, "label": v[0], "color": v[2]}
                             for k, v in build.PALETTES.items()],
                "fonts": [{"key": k, "label": v[0]} for k, v in build.FONTS.items()],
                "defaults": {"layout": DEFAULT_LAYOUT, "palette": DEFAULT_PALETTE,
                             "font": DEFAULT_FONT},
            }
            self._send(200, json.dumps(body, ensure_ascii=False).encode(),
                       "application/json; charset=utf-8")
        elif url.path == "/photo":
            photo = ROOT / "photo.png"
            if not photo.exists():
                self._send(404, b"no photo", "text/plain; charset=utf-8")
                return
            self._send(200, photo.read_bytes(), "image/png")
        elif url.path in ("/pdf", "/draft"):
            q = parse_qs(url.query)
            layout = q.get("layout", [DEFAULT_LAYOUT])[0]
            palette = q.get("palette", [DEFAULT_PALETTE])[0]
            font = q.get("font", [DEFAULT_FONT])[0]
            if (layout not in build.LAYOUTS or palette not in build.PALETTES
                    or font not in build.FONTS):
                self._send(400, b"unknown layout/palette/font", "text/plain; charset=utf-8")
                return
            path = self.draft_pdf(layout, palette, font)
            if path is None:
                return
            self._send(200, path.read_bytes(), "application/pdf")
        else:
            self._send(404, b"not found", "text/plain; charset=utf-8")

    def draft_pdf(self, layout: str, palette: str, font: str):
        """按需渲染任意组合并缓存；内容或样式改动后自动重渲。"""
        draft = build.BUILD / f"export-{layout}-{palette}-{font}.pdf"
        sources = [YML, ROOT / "photo.png", SCRIPT_DIR / "base.css",
                   SCRIPT_DIR / "template.html.j2",
                   SCRIPT_DIR / "layouts" / build.LAYOUTS[layout][1],
                   SCRIPT_DIR / "layouts" / build.LAYOUTS[layout][2],
                   SCRIPT_DIR / "palettes" / build.PALETTES[palette][1],
                   SCRIPT_DIR / "fonts" / build.FONTS[font][1]]
        src_mtime = max(p.stat().st_mtime for p in sources if p.exists())

        def fresh():
            return draft.exists() and draft.stat().st_mtime >= src_mtime

        if not fresh():
            try:
                with _lock:
                    if not fresh():
                        build.DATA = yaml.safe_load(YML.read_text(encoding="utf-8"))
                        html = build.render_html(layout, palette, font)
                        build.make_pdf(html, draft)
            except Exception as exc:  # 生成失败（如 Edge 异常）
                self._send(500, f"生成失败：{exc}".encode(), "text/plain; charset=utf-8")
                return None
        return draft

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/api/save", "/api/export", "/api/export-docx", "/api/photo"):
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)

        if path == "/api/photo":
            self.save_photo(raw)
            return

        payload = json.loads(raw.decode("utf-8"))
        data = payload.get("data") or {}

        if not str(data.get("name", "")).strip() or not str(data.get("intent", "")).strip():
            self._send(400, json.dumps(
                {"ok": False, "msg": "姓名和求职意向不能为空"}, ensure_ascii=False).encode(),
                "application/json; charset=utf-8")
            return

        if path == "/api/export":
            self.export_one(data, payload.get("layout", DEFAULT_LAYOUT),
                            payload.get("palette", DEFAULT_PALETTE),
                            payload.get("font", DEFAULT_FONT))
            return

        if path == "/api/export-docx":
            self.export_docx(data)
            return

        with _lock:
            if YML.exists():
                shutil.copy2(YML, BAK)
            YML.write_text(dump_yaml(data), encoding="utf-8")
            stamp = int(YML.stat().st_mtime)

        self._send(200, json.dumps({
            "ok": True, "msg": "已应用更改", "stamp": stamp,
        }, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def save_photo(self, raw: bytes):
        """接收上传的图片，统一转成 PNG 存为 photo.png（纠正方向、限宽 720）"""
        if not raw:
            self._send(400, json.dumps({"ok": False, "msg": "没有收到图片"},
                                       ensure_ascii=False).encode(),
                       "application/json; charset=utf-8")
            return
        if len(raw) > 15 * 1024 * 1024:
            self._send(400, json.dumps({"ok": False, "msg": "图片过大，请控制在 15MB 以内"},
                                       ensure_ascii=False).encode(),
                       "application/json; charset=utf-8")
            return
        try:
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
            if img.width > 720:
                img = img.resize((720, round(img.height * 720 / img.width)), Image.LANCZOS)
            img.save(ROOT / "photo.png", "PNG")
        except Exception as exc:
            self._send(400, json.dumps({"ok": False, "msg": f"无法识别图片：{exc}"},
                                       ensure_ascii=False).encode(),
                       "application/json; charset=utf-8")
            return
        self._send(200, json.dumps({"ok": True, "msg": "照片已更新"},
                                   ensure_ascii=False).encode(),
                   "application/json; charset=utf-8")

    def export_one(self, data: dict, layout: str, palette: str, font: str):
        """只生成当前选中的一个「版式 + 配色 + 字体」，导出为独立文件，不覆盖母版。"""
        if (layout not in build.LAYOUTS or palette not in build.PALETTES
                or font not in build.FONTS):
            self._send(400, json.dumps({"ok": False, "msg": "未知版式、配色或字体"},
                                       ensure_ascii=False).encode(),
                       "application/json; charset=utf-8")
            return
        try:
            with _lock:
                if YML.exists():
                    shutil.copy2(YML, BAK)
                YML.write_text(dump_yaml(data), encoding="utf-8")
                build.DATA = yaml.safe_load(YML.read_text(encoding="utf-8"))
                html = build.render_html(layout, palette, font)
                out = build.BUILD / f"export-{layout}-{palette}-{font}.pdf"
                build.make_pdf(html, out)
                pdf_bytes = out.read_bytes()
        except Exception as exc:  # 生成失败（如 Edge 异常）
            self._send(500, json.dumps({"ok": False, "msg": f"生成失败：{exc}"},
                                       ensure_ascii=False).encode(),
                       "application/json; charset=utf-8")
            return
        self._send(200, pdf_bytes, "application/pdf")

    def export_docx(self, data: dict):
        """按当前表单内容生成 Word，写到 build/ 下临时文件后回传，不覆盖母版。"""
        try:
            with _lock:
                build.DATA = data
                prev = build.DOCX_OUT
                build.DOCX_OUT = build.BUILD / "export.docx"
                try:
                    build.make_docx()
                    body = build.DOCX_OUT.read_bytes()
                finally:
                    build.DOCX_OUT = prev
        except Exception as exc:
            self._send(500, json.dumps({"ok": False, "msg": f"生成失败：{exc}"},
                                       ensure_ascii=False).encode(),
                       "application/json; charset=utf-8")
            return
        self._send(200, body,
                   "application/vnd.openxmlformats-officedocument.wordprocessingml.document")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="简历内容目录（含 resume.yml / photo.png）")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()
    global ROOT, YML, BAK
    ROOT = Path(args.root).resolve()
    YML = ROOT / "resume.yml"
    BAK = ROOT / "resume.yml.bak"
    build.configure(ROOT)
    if not YML.exists():
        raise SystemExit(f"未找到 {YML}，请先运行 init.py 初始化")
    url = f"http://127.0.0.1:{args.port}/"
    print(f"编辑器已启动：{url}（Ctrl+C 退出）")
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
