# 排版与配色

## 层级变量
`scripts/fonts/*.css` 只定义四个变量，`base.css` 与各版式通过变量引用：

| 变量 | 作用对象 |
| --- | --- |
| `--display-font` | 姓名 |
| `--head-font` | 章节标题、公司名、能力标签 |
| `--body-font` | 正文、bullet、概述 |
| `--num-font` | 日期、编号、英文小标（统一 Georgia） |

字号与 `--name-weight` 由配色文件控制，字体文件不要写字号。

## 6 组字体
| key | 名称 | 组合 |
| --- | --- | --- |
| songhei | 宋黑对照 | 思源宋体标题 + 微软雅黑正文 |
| quansong | 全宋典雅 | 华文中宋标题 + 思源宋体正文 |
| yahei | 雅黑现代 | 全微软雅黑 |
| dengxian | 等线清爽 | 全等线 DengXian，字形窄、轻 |
| editorial | 黑标宋文 | 雅黑标题 + 宋体正文 |
| lightsans | 细黑雅致 | 华文细黑标题 + 思源黑正文，姓名不加粗 |

## 6 种配色
| key | 名称 | 主色 |
| --- | --- | --- |
| ink | 墨黑 | `#1B2228` |
| gold | 鎏金 | `#C0A265` |
| navy | 黛蓝 | `#22405F` |
| burgundy | 绛红 | `#7B2E3C` |
| forest | 墨绿 | `#2E5A48` |
| slate | 烟灰 | `#6C7681` |

配色只改变量，不改布局。章节中文标题 `.sec .zh` 使用 `var(--accent)`，切换配色时整页主色随之变化。

## 原则
- 一份简历最多两种字族：标题与正文靠字族或字重形成对比，不靠颜色。
- 中文用黑体或宋体；数字与英文统一 Georgia，避免视觉跳动。
- 全文只用一种主色 + 黑灰层级，正文不染色。
- 正文 9pt 左右，行距 1.3；姓名 24pt 左右；章节标题 11.5pt 左右。
- 字体必须在本机存在。Windows 常见可用：微软雅黑、等线、华文中宋、华文细黑、思源宋体/黑体、楷体、仿宋；没有 SimSun/SimHei 时不要写这两个名字。
- 改字体只改 `scripts/fonts/` 下的变量文件，不要在版式 CSS 里写死 `font-family`。

## 默认组合（也是母版清单）
classic+ink+songhei、sidebar+navy+songhei、band+forest+yahei、
timeline+burgundy+songhei、grid+gold+dengxian、centered+slate+quansong。
