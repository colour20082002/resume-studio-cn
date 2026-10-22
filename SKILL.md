---
name: resume-studio
description: 中文简历制作与优化工作台。把简历内容写成 resume.yml，用 6 种版式 × 6 种配色 × 6 组字体生成 A4 PDF 与可编辑 Word，并附带网页可视化编辑器。用户要做简历、改简历、按 JD 定制、调排版/配色/字体、导出 PDF/Word 时使用。
---

# Resume Studio

内容与样式分离的中文简历流水线：`resume.yml` 是唯一内容源，HTML/CSS 负责版式，Edge 无头打印出 PDF，python-docx 出 Word。所有脚本自包含，不依赖外部项目。

## 目录

```
resume-studio/
├── SKILL.md
├── assets/starter/resume.yml     # 初始化模板（占位内容）
├── references/                   # 写作、定制、版式、排版、检查清单
└── scripts/
    ├── init.py                   # 复制起始 resume.yml
    ├── build.py                  # PDF / PNG / Word 生成
    ├── check.py                  # 结构 + 页数 + 关键词校验
    ├── editor.py / editor.html   # 网页编辑器
    ├── base.css / template.html.j2
    ├── layouts/                  # 6 种版式
    ├── palettes/                 # 6 种配色
    └── fonts/                    # 6 组字体
```

内容目录（默认当前工作目录）只需要 `resume.yml`，可选 `photo.png`；`build/` 存放中间产物。

`assets/starter/resume.yml` 是一份完整的虚构示例（行政运营人员，人物/公司/学校/联系方式均系编造），初始化后可直接生成 PDF 预览效果；正式使用时把全部字段替换为真实信息。

## 快速开始

```bash
# 1. 初始化内容目录（不覆盖已有 resume.yml）
py -3 scripts/init.py --root "D:\resume"

# 2. 编辑 resume.yml 后生成 6 份母版 PDF + Word
py -3 scripts/build.py all --root "D:\resume"

# 只出 PDF / 只出 Word / 出预览截图
py -3 scripts/build.py pdf --root "D:\resume"
py -3 scripts/build.py docx --root "D:\resume"
py -3 scripts/build.py png --root "D:\resume"

# 3. 校验（页数、每页首尾行、JD 关键词）
py -3 scripts/check.py --root "D:\resume" --pages 2 --keywords "客户服务,风控,数据分析"

# 4. 网页编辑器（浏览器里改内容、切版式/配色/字体、导出）
py -3 scripts/editor.py --root "D:\resume" --port 8765
```

路径参数始终指向**内容目录**，脚本资源从自身目录读取，可在任意 cwd 运行。

## 内容结构（resume.yml）

```yaml
name: 姓名
intent: 目标岗位 / 方向
meta: [性别 · 年龄, 政治面貌, 城市, 到岗时间]
contact: [手机, 邮箱]
show_photo: true
summary: 一段式自我概述
competencies: [{label, text}]        # 4–6 条
experience: [{company, date, role, industry, bullets: [{label, text}]}]
education: [{school, date, major, degree, detail}]
certificates: [证书]
```

字段写错会由 `check.py` 直接报出，不需要猜。

## 工作流

**新做一份简历**
1. `init.py` 初始化 → 读 `references/writing-rules.md` 填内容。
2. 读 `references/layout-guide.md` 选版式，`references/typography.md` 选配色与字体。
3. `build.py` 出 PDF → `check.py` 校验 → 打开 PDF 目测分页。
4. 用 `editor.py` 微调，或直接改 `resume.yml` 后重跑。

**优化已有简历 / 按 JD 定制**
1. 读 `references/tailoring.md`，提取 JD 关键词并做证据映射。
2. 只改 `resume.yml` 的顺序与措辞，不改样式代码。
3. `check.py --keywords` 确认关键词命中，`--pages 2` 确认页数。
4. 过一遍 `references/checklist.md` 再交付。

**只调样式**
- 版式：`scripts/layouts/*.css`；配色：`scripts/palettes/*.css`（只改变量）；字体：`scripts/fonts/*.css`（只改四个字体变量）。
- 不要在版式 CSS 里写死 `font-family` 或改 `@page`。
- 大块经历容器不能加 `break-inside: avoid`，否则会从 2 页撑到 3 页。

## 依赖
- Python 3.10+：`pyyaml`、`jinja2`、`python-docx`、`pillow`、`pypdf`
- Microsoft Edge（`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`）用于打印 PDF；路径不符时改 `build.py` 顶部 `EDGE`
- 中文字体需本机存在，可用清单见 `references/typography.md`

## 参考文件
- `references/writing-rules.md` — bullet/summary/能力条目的写法与中文排版规范
- `references/tailoring.md` — 按 JD 定制的流程、评分与边界
- `references/layout-guide.md` — 6 种版式的适用场景与分页规则
- `references/typography.md` — 字体层级变量、6 组字体、6 种配色
- `references/checklist.md` — 交付前检查清单
