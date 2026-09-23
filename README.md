# X Made Easy Skill

一个中文写作 skill：仿 Silvanus P. Thompson《Calculus Made Easy》(1910) 的教学精神，把任意主题写成一本"轻松学"小书。

它的核心不是把知识讲得更满，而是先替读者驱除预备恐惧：把术语脱西装，把符号翻成人话，先讲直觉，再讲规矩。

## 汤普森是怎么写的

一百多年前，汤普森这样开始讲微积分（引自 1914 年第二版，中文是意译）：

> The preliminary terror, which chokes off most fifth-form boys from even attempting to learn how to calculate, can be abolished once for all by simply stating what is the meaning—in common-sense terms—of the two principal symbols that are used in calculating.
>
> 那种把大多数中学生噎得连试都不敢试的预备恐惧，可以一劳永逸地除掉，办法只是用常识的话说清楚：微积分里最主要的两个符号是什么意思。

然后他说，d 的意思不过是"一小点儿"；∫ 不过是一个拉长的 S，意思是"……的总和"。讲完，第一章就结束了，最后一句是：

> That's all.

这个 skill 学的就是这个动作：找到读者怕的那几个符号和术语，一个一个说穿，然后收手。

## 一本书怎么长出来

1. **摸清读者怕什么**：读者现在会什么，最怕哪 5–10 个术语或符号，学完要亲手做成哪件事。
2. **先出骨架**：`00-目录与体例.md`，交你看风格和深浅，对路了再写正文。
3. **逐章写**，每章五段：开篇除恐 → 白话化 → 直觉先行（说清什么可以先不管）→ 贴身例子与章末练习 → "这一章要带走的东西"，最后一句"就这样。"
4. **写附录**：术语词典、一页纸速查、练习答案、我们抄过的近路、出处说明。
5. **自检，出 PDF**。

三条铁律：是驱除恐惧，不是写教科书；事实核查，绝不捏造出处；不堆排比、不用感叹号、不说"显然"。

## 目录

```
SKILL.md                    skill 主说明与工作流
references/style-guide.md   风格 DNA：汤普森原话、除恐开篇、脱西装四步、抄近路记账、目录模板
references/pdf-build.md     合成 PDF 的两条路线（网页 / LaTeX）和踩过的坑
scripts/check_book.py       书稿自检：感叹号、"显然"类禁词、五段式收尾、例子出处、开篇雷同
scripts/build_pdf.sh        一条命令出 PDF（pandoc + Chrome/Chromium）
scripts/book.css            PDF 样式，中文字体按 macOS / Windows / Linux 依次回退
```

## 安装

Claude Code：

```bash
git clone https://github.com/baibanbao/x-made-easy-skill ~/.claude/skills/x-made-easy-skill
```

只想在某个项目里用，就放进那个项目的 `.claude/skills/`。别的能读 skill 的工具（如 Codex），放进它读取 skills 的目录即可。

然后用类似这些话触发：

- "用轻松学风格教我 X"
- "仿《Calculus Made Easy》写一本 X 入门书"
- "用 x-made-easy 做一本 X 轻松学"

## 自检与出 PDF

```bash
python3 scripts/check_book.py ~/X轻松学            # 查书稿，只用 Python 标准库
scripts/build_pdf.sh ~/X轻松学 "X轻松学"            # 要 pandoc 和 Chrome/Chromium/Edge
```

自检报"错"的必须改，报"提醒"的逐条看。PDF 的细节和 LaTeX 精排见 `references/pdf-build.md`。

## English

A Chinese writing skill for Claude that turns any intimidating subject into a small "Made Easy" book, in the spirit of Silvanus P. Thompson's *Calculus Made Easy* (1910). It first names what scares the reader, strips each term down to plain words, tells the reader what can safely be ignored for now, teaches with small worked examples, and ends each chapter with a short "That's all." Output is one Markdown file per chapter, plus a checker script and a one-command PDF build. Chinese by default; it follows the user's language if asked in another.

更新记录见 [CHANGELOG.md](CHANGELOG.md)。

## 许可

MIT License。
