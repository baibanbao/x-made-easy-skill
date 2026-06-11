# X Made Easy Skill

一个中文写作 skill：仿 Silvanus P. Thompson《Calculus Made Easy》(1910) 的教学精神，把任意主题写成一本"轻松学"小书。

它的核心不是把知识讲得更满，而是先替读者驱除预备恐惧：把术语脱西装，把符号翻成人话，先讲直觉，再讲规矩。

## 适合做什么

- 把一个吓人的主题写成分章 Markdown 教学书
- 先产出 `00-目录与体例.md`，确认风格和深浅
- 按五段式逐章推进：开篇除恐、白话化、直觉先行、贴身例子、短收尾
- 最后补 `99-结语与附录.md`
- 按参考流程合成 PDF

## 目录

- `SKILL.md`：skill 主说明与工作流
- `references/style-guide.md`：风格 DNA、目录模板、例题规矩
- `references/pdf-build.md`：Markdown 合成 PDF 的两条路线

## 安装

把整个目录放到 Claude/Codex 可读取的 skills 目录中，例如：

```bash
~/.claude/skills/x-made-easy-skill
```

然后用类似这些话触发：

- "用轻松学风格教我 X"
- "仿《Calculus Made Easy》写一本 X 入门书"
- "用 x-made-easy 做一本 X 轻松学"

## 许可

MIT License。
