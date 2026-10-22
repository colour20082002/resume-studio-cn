# Resume Studio CN

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-0078D4?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)

> 把简历写成一份 YAML，生成 216 种排版组合的中文简历，同时输出 A4 PDF 与可编辑 Word。

**Resume Studio CN** 是一个内容与样式彻底分离的中文简历流水线：一份 `resume.yml`，6 种版式 × 6 种配色 × 6 组字体自由组合，附带网页可视化编辑器、页数与关键词校验，以及按 JD（职位描述）定制简历的完整工作流。

排版、渲染、校验、导出全部在本地完成，脚本本身不发起任何网络请求，也不需要账号或在线服务。简历的撰写与按 JD 改写由你所使用的 Agent / 大模型客户端完成，这部分内容会按该服务商的隐私政策发送给模型；不接 AI 也能纯手工使用全部排版与导出功能。

---

## 功能特性

- **一份内容，多种成品**：`resume.yml` 是唯一内容源，改内容不用碰 HTML/CSS。
- **216 种排版组合**：6 版式 × 6 配色 × 6 组字体，任意组合即时预览。
- **PDF + Word 双产出**：Edge 无头打印出精确 A4 分页；python-docx 出可继续编辑、可贴证件照的 Word。
- **按 JD 定制**：从职位描述提取硬性要求、职责动词、结果指标，映射到真实经历后重排顺序与措辞，不改事实。
- **自动校验**：YAML 结构、PDF 页数、每页首尾行、JD 关键词命中，交付前给出 PASS / FAIL。
- **网页编辑器**：浏览器内改内容、切版式/配色/字体、实时预览、上传头像、一键导出。
- **Agent Skill**：可直接放入 Trae 等支持 Skill 的 Agent 环境，用自然语言驱动整套流程。

## 环境要求

| 项目 | 要求 |
| --- | --- |
| 操作系统 | Windows（依赖 Microsoft Edge 打印 PDF） |
| Python | 3.10+ |
| Edge | 默认 `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` |
| 中文字体 | 思源宋体/黑体、微软雅黑、等线、华文中宋、华文细黑等（缺失时对应组合回退） |

## 安装

```bash
git clone https://github.com/colour20082002/resume-studio-cn.git
cd resume-studio-cn
pip install pyyaml jinja2 python-docx pillow pypdf
```

## 快速开始

```bash
# 1. 初始化内容目录（生成示例 resume.yml，不覆盖已有文件）
py -3 scripts/init.py --root "D:\resume"

# 2. 打开 resume.yml，把示例内容换成你的真实经历
#    然后生成 6 份母版 PDF + 一份 Word
py -3 scripts/build.py all --root "D:\resume"

# 3. 校验页数与关键词
py -3 scripts/check.py --root "D:\resume" --pages 2 --keywords "客户服务,数据分析"

# 4. 打开网页编辑器做微调
py -3 scripts/editor.py --root "D:\resume"
```

产物默认写在内容目录：

```
D:\resume\
├── resume.yml
├── photo.png              # 可选，证件照
├── 个人简历-经典-墨黑-宋黑对照.pdf
├── 个人简历-左栏-黛蓝-宋黑对照.pdf
├── 个人简历-色带-墨绿-雅黑现代.pdf
├── 个人简历-时间轴-绛红-宋黑对照.pdf
├── 个人简历-卡片-鎏金-等线清爽.pdf
├── 个人简历-居中-烟灰-全宋典雅.pdf
├── 个人简历.docx
└── build\                 # 中间 HTML 与预览截图
```

## 简历内容结构

`resume.yml` 字段如下，写错会被 `check.py` 直接指出。示例中的公司、学校、城市均以 `XX` 占位，人物与联系方式为虚构内容：

```yaml
name: 周雨桐
intent: 行政运营 / 办公室管理        # 求职意向
meta:
  - 女 · 31 岁
  - XX 市
  - 一周内到岗
contact:
  - 138 0000 0000
  - zhouyutong@example.com
show_photo: true                    # 是否显示证件照

summary: 8 年行政与运营经验……        # 一段式概述，80–140 字

competencies:                       # 4–6 条
  - label: 行政统筹
    text: 职场管理 · 资产盘点 · 采购比价 · 供应商管理

experience:                         # 时间倒序
  - company: XX 数字科技有限公司
    date: 2021.03 – 2025.12
    role: 行政主管
    industry: 互联网服务
    bullets:
      - label: 职场管理
        text: 统筹 3 处办公场地共 1200 ㎡ 的日常运维……

education:
  - school: XX 学院
    date: 2012.09 – 2016.06
    major: 行政管理
    degree: 本科
    detail: 主修课程：……

certificates:
  - XX 职业资格证书
```

写作要点（完整规则见 [`references/writing-rules.md`](references/writing-rules.md)）：

- `summary` 一段 80–140 字：年限与行业 → 可验证的优势 → 带数字的成果 → 求职方向。
- 每条 bullet 20–50 字，动词开头，有结果、有数字，一条只讲一件事。
- `label` 用 2–6 字概括职责，全文不重复。
- 核心能力 4–6 条，每个关键词都能在经历里找到证据。
- 中文与英文/数字之间加半角空格；日期统一 `YYYY.MM – YYYY.MM`。
- 不编造公司、职位、时间、数字、证书。

## 命令参考

所有脚本用 `--root` 指定**内容目录**，模板与样式从脚本自身目录读取，可在任意工作目录运行。

| 命令 | 作用 |
| --- | --- |
| `py -3 scripts/init.py --root <目录>` | 初始化内容目录；已存在 `resume.yml` 时拒绝覆盖，加 `--force` 才覆盖 |
| `py -3 scripts/build.py all --root <目录>` | 生成 6 份母版 PDF + Word |
| `py -3 scripts/build.py pdf --root <目录>` | 只生成 6 份 PDF |
| `py -3 scripts/build.py docx --root <目录>` | 只生成 Word |
| `py -3 scripts/build.py png --root <目录>` | 生成 6 张整页预览截图（`build/preview-*.png`） |
| `py -3 scripts/check.py --root <目录> --pages 2 --keywords "a,b,c"` | 校验结构 / 页数 / 每页首尾行 / 关键词 |
| `py -3 scripts/editor.py --root <目录> [--port 8765] [--no-browser]` | 启动网页编辑器 |

`build.py` 支持 `--out <目录>` 把产物输出到别处，内容目录保持不变。

## 版式 / 配色 / 字体

**版式**（`scripts/layouts/`）

| key | 名称 | 适用场景 |
| --- | --- | --- |
| `classic` | 经典 | 通用、国企/传统行业，内容量中等 |
| `sidebar` | 左栏 | 信息密集、经历多，突出技能与联系方式 |
| `band` | 色带 | 市场 / 运营 / 销售，视觉记忆点强 |
| `timeline` | 时间轴 | 经历连续、跨度长，强调成长线 |
| `grid` | 卡片 | 转行、技能型岗位、内容偏少 |
| `centered` | 居中 | 精简一页、管理岗，风格克制 |

**配色**（`scripts/palettes/`）：墨黑 `#1B2228`、鎏金 `#C0A265`、黛蓝 `#22405F`、绛红 `#7B2E3C`、墨绿 `#2E5A48`、烟灰 `#6C7681`。配色只改 CSS 变量，不改变布局。

**字体**（`scripts/fonts/`）

| key | 名称 | 组合 |
| --- | --- | --- |
| `songhei` | 宋黑对照 | 思源宋体标题 + 微软雅黑正文 |
| `quansong` | 全宋典雅 | 华文中宋标题 + 思源宋体正文 |
| `yahei` | 雅黑现代 | 全微软雅黑 |
| `dengxian` | 等线清爽 | 全等线 DengXian，字形更窄更轻 |
| `editorial` | 黑标宋文 | 雅黑标题 + 宋体正文 |
| `lightsans` | 细黑雅致 | 华文细黑标题 + 思源黑正文，姓名不加粗 |

排版原则：一份简历最多两种字族；标题与正文靠字族或字重形成对比，不靠颜色；数字与英文统一 Georgia，避免视觉跳动。

## 按 JD 优化简历

目标不是换一份简历，而是让同一批真实经历按目标岗位的优先级重新排序、重新措辞。

1. **提取 JD 关键词**：硬性要求（行业、年限、证书、工具）、职责动词（搭建、统筹、分析、推动）、结果指标（坏账率、满意度、转化率、成本）。
2. **做证据映射**：每个关键词在 `resume.yml` 里找到一条真实经历；找不到的不要硬编。
3. **重排顺序**：`summary` 首句改成岗位方向；`competencies` 把最相关的 3 条提到前面；每段经历把最贴近 JD 的 bullet 放第一条。
4. **对齐措辞**：JD 说「客户服务」，简历就不要只写「客诉处理」；只改词，不改事实。
5. **跑校验**：

```bash
py -3 scripts/check.py --root "D:\resume" --pages 2 --keywords "客户服务,数据分析,团队管理"
```

关键词全部命中且页数符合预期才交付。评分参考、边界与完整流程见 [`references/tailoring.md`](references/tailoring.md)，交付前过一遍 [`references/checklist.md`](references/checklist.md)。

跨方向投递时复制整个内容目录再改，不要在一份 `resume.yml` 里塞两个方向。

## 网页编辑器

```bash
py -3 scripts/editor.py --root "D:\resume" --port 8765
```

打开 `http://127.0.0.1:8765/`：

- 左侧改基本信息、概述、能力、经历、教育、证书；
- 顶部切换版式 / 配色 / 字体，右侧实时预览当前组合的 PDF；
- 可上传证件照（自动纠正方向、限宽 720），可一键隐藏/显示头像；
- 「应用更改」只写入 `resume.yml`（自动备份 `resume.yml.bak`）并刷新预览；
- 「保存并导出 PDF」只生成当前选中的组合，弹出另存为窗口，不覆盖已有母版。

预览按需渲染并缓存到 `build/export-<版式>-<配色>-<字体>.pdf`，内容或样式文件改动后会自动重渲。

## 项目结构

```
resume-studio-cn/
├── SKILL.md                      # Agent Skill 入口说明
├── README.md
├── LICENSE
├── assets/starter/resume.yml     # 初始化模板（虚构示例，XX 占位）
├── references/
│   ├── writing-rules.md          # 内容写作与中文排版规范
│   ├── tailoring.md              # 按 JD 定制的流程与边界
│   ├── layout-guide.md           # 6 种版式与分页规则
│   ├── typography.md             # 字体层级、6 组字体、6 种配色
│   └── checklist.md              # 交付前检查清单
└── scripts/
    ├── init.py                   # 初始化内容目录
    ├── build.py                  # PDF / PNG / Word 生成
    ├── check.py                  # 结构 + 页数 + 关键词校验
    ├── editor.py                 # 网页编辑器服务
    ├── editor.html
    ├── base.css                  # 公共骨架（@page 尺寸与边距）
    ├── template.html.j2          # 外壳模板
    ├── layouts/                  # 6 种版式 html + css
    ├── palettes/                 # 6 种配色（仅 CSS 变量）
    └── fonts/                    # 6 组字体（仅字体变量）
```

## 常见问题

**PDF 撑到 3 页？**
不要给 `.job`、`.tl-item`、卡片这类大块容器加 `break-inside: avoid`，否则整块被推到下一页。允许在 bullets 之间断页。

**Edge 打印失败？**
检查 `scripts/build.py` 顶部的 `EDGE` 路径是否与安装位置一致。截图功能还需独立 `--user-data-dir`，脚本已内置，不要去掉。

**字体显示成方块？**
对应字体未安装或字体名不存在（如 Windows 常缺 SimSun/SimHei）。换一组字体，或修改 `scripts/fonts/*.css` 中的字体变量。

**关键词明明写了却报未命中？**
`check.py` 比对的是 `resume.yml` 原文，需与简历里的写法完全一致（如「办公区搬迁」与「办公区整体搬迁」不同）。改关键词或统一措辞。

**照片不显示？**
内容目录下需要有 `photo.png`，且 `resume.yml` 中 `show_photo` 不为 `false`。

**端口被占用？**
换 `--port`，例如 `--port 8790`。

## 隐私与数据流

| 环节 | 运行位置 | 是否联网 |
| --- | --- | --- |
| 排版、渲染 PDF / Word | 本机 Python + Edge 无头打印 | 否 |
| 页数、空页、关键词校验 | 本机 | 否 |
| 网页编辑器（含头像上传） | 本机 `127.0.0.1`，只读写本地文件 | 否 |
| 撰写经历、按 JD 改写措辞 | 你所选的 Agent / 大模型客户端 | 是，内容会发送给该模型服务商 |

介意隐私时，可先用占位符跑完 AI 环节，再在本地 `resume.yml` 填回手机号、住址等信息；排版与导出也可以完全不接 AI，纯手工完成。

## 设计取舍

- **内容与样式分离**：所有文字只在 `resume.yml`；改样式只动 `layouts/`、`palettes/`、`fonts/`，互不干扰。
- **配色只改变量**：切换配色时布局完全不变，降低组合爆炸带来的维护成本。
- **字体文件只管字体**：字号与字重归配色文件，避免同一属性两处定义。
- **不做自动投递**：只负责把简历做好，投递由用户自己完成。
- **只校验能验证的东西**：页数、空页、每页首尾行、关键词命中；审美与措辞仍需人看。

## 在 Trae 中作为 Skill 使用

本仓库同时是一个 Agent Skill。克隆到项目的 `.trae/skills/resume-studio/` 或全局 Skill 目录后，在 Trae 中直接说「帮我改简历」「按这个 JD 定制」「导出 PDF」即可触发，Agent 会按 `SKILL.md` 的流程调用 `init.py` / `build.py` / `check.py` / `editor.py`。

不使用 Agent 也可以完全按上面的命令手动操作，两者能力一致。

## 贡献

欢迎提交 Issue 和 Pull Request：新增版式/配色/字体组合、修复分页问题、补充写作规则都可以。提交前请确保 `scripts/build.py all` 与 `scripts/check.py` 能跑通，并说明改动影响的组合。

## 许可证

[MIT](LICENSE) © Resume Studio contributors
