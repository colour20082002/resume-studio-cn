# 版式指南

10 种版式定义在 `scripts/layouts/`，每种由 `*.html.j2` 与 `*.css` 组成，共用 `scripts/base.css` 骨架。

| key | 名称 | 结构 | 适用 |
| --- | --- | --- | --- |
| classic | 经典 | 单栏通排，章节标题左侧竖线 | 通用、国企/传统行业、内容量中等 |
| sidebar | 左栏 | 左侧深色栏放照片/联系方式/能力 | 信息密集、经历多、需要突出技能 |
| band | 色带 | 页首整幅色带承载姓名与联系方式 | 市场/运营/销售，视觉记忆点强 |
| timeline | 时间轴 | 经历沿时间轴排布 | 经历连续、跨度长、强调成长线 |
| grid | 卡片 | 能力与经历卡片化 | 转行、技能型岗位、内容较少 |
| centered | 居中 | 姓名与章节标题居中 | 精简一页、管理岗、风格克制 |
| table | 表格式 | 页首信息成行、章节标题带底色条、能力细线分隔 | 银行/国企/外企，条目多、要求整齐 |
| rightbar | 右栏 | 右侧深色窄栏放技能与证书，左侧全宽写经历 | 技能/证书是卖点，经历文字量较大 |
| minimal | 极简 | 只有细线与留白，无底色块 | 设计/研发/互联网，弱装饰 |
| datebar | 日期栏 | 左侧日期列 + 竖向分隔线，右侧正文 | 时间跨度长，突出时间线节拍 |

## 选版式
- 内容多、要压到 2 页：classic、sidebar、rightbar。
- 想突出个人品牌：band、timeline。
- 内容少、不想显得空：grid、centered。
- 要求整齐、偏传统行业：table、datebar。
- 弱化装饰、突出内容：minimal。
- 不确定时用 classic + ink，最稳。

## 分页规则
- 页面 A4，`base.css` 已设 @page 尺寸与边距，不要在版式里改页宽。
- 大块容器（`.job`、`.tl-item`、卡片）**不能**加 `break-inside: avoid`，否则整块被推到下一页，页数会从 2 页变 3 页。
- 允许在 bullets 之间断页；断页后第二页顶部不能是孤立的章节标题。
- 目标：两页基本均衡。第一页正文接近页底，第二页留白不超过 3–4 行。

## 校验方法
```bash
py -3 scripts/build.py pdf --root <内容目录>
py -3 scripts/check.py --root <内容目录> --pages 2
```
`check.py` 会打印每页首尾行，据此判断分页点是否合理。

## 截图预览
```bash
py -3 scripts/build.py png --root <内容目录>
```
产物在 `<内容目录>/build/preview-<layout>-<palette>-<font>.png`。
Edge 截图必须带独立 `--user-data-dir`，脚本已内置，不要去掉。
