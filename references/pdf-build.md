# 把书稿合成 PDF（中文 + 数学）

两条路线。书里有数学公式且要排版精致 → 走 **B（LaTeX）**；只有中文、要快要稳 → 走 **A（网页）**。两本样书都用过。

依赖：`pandoc`（macOS `brew install pandoc`，Debian/Ubuntu `apt install pandoc`）；A 用 Chrome、Chromium 或 Edge；B 用 `xelatex`。

## 最省事：一条命令（路线 A）

```bash
scripts/build_pdf.sh "/path/to/书文件夹" "书名"
```

PDF 写到 `书文件夹/书名.pdf`。脚本自己找浏览器，找不到就用环境变量指定：`CHROME=/path/to/chrome scripts/build_pdf.sh ...`。样式在 `scripts/book.css`，字体按 macOS / Windows / Linux 依次回退。脚本在 Linux + Chromium 上实测过（以 root 身份运行时会自动加 `--no-sandbox`）；它用的命令就是下面的路线 A，那套命令在 macOS 上验证过；Windows 没测过。

脚本做的事就是下面路线 A 的几步，另外处理了几件麻烦事：文件名带空格、只收 `NN-章名.md`、图片嵌进 PDF、pandoc 转不动的公式会在终端报出来。

---

## 手动拼接

只收两位数字前缀的分章文件，按 C 排序，文件名带空格也不怕：

```bash
cd "/path/to/书文件夹"
export LC_ALL=C
: > /tmp/combined.md
first=1
for f in [0-9][0-9]-*.md; do
  # LaTeX 路线才插分页；网页路线靠 CSS h1 分页，可省下面这行
  if [ $first -eq 0 ]; then printf '\n\n```{=latex}\n\\newpage\n```\n\n' >> /tmp/combined.md; fi
  cat "$f" >> /tmp/combined.md; printf '\n\n' >> /tmp/combined.md; first=0
done
```

---

## 路线 A：网页版（pandoc → HTML+MathML → Chrome 打印）

数学走 Chrome 原生 MathML，不联网。容错最高，中文代码块、中文标点都不出问题。

```bash
pandoc /tmp/combined.md -f markdown+lists_without_preceding_blankline-blank_before_blockquote \
  -t html5 -s --mathml --embed-resources --resource-path=. \
  -c scripts/book.css --metadata pagetitle="书名" -o /tmp/book.html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --run-all-compositor-stages-before-draw --virtual-time-budget=15000 \
  --print-to-pdf="书名-网页版.pdf" "file:///tmp/book.html"
```

`scripts/book.css` 关键项：正文宋体、标题黑体、代码等宽，三个平台各有回退字体；`h1{page-break-before:always}` 每章分页（首个 `h1:first-of-type{page-break-before:avoid}`）；`@page{size:A4;margin:20mm 18mm}`；`pre{white-space:pre-wrap}`；例题引用块红边浅底。

**坑**：

1. **pandoc 转不了 `\dbinom`。** pandoc 3.9 实测：`\dfrac` 已能转，`\dbinom` 仍会原样吐出 TeX 文本。改用 `\binom`。旧版 pandoc 连 `\dfrac` 也不认，改用 `\frac`。
2. **列表前没空行，会糊成一段。** "计数\n- 第一条\n- 第二条"在 pandoc 默认读法里是一段话，印出来成了"计数 - 第一条 - 第二条"。模型写的稿子常这样。读入格式加 `+lists_without_preceding_blankline` 就好，脚本已经加了。
3. **别给公式改 `display`。** CSS 里写 `math[display="block"]{display:block}` 会覆盖 Chrome 默认的公式排版，独立公式缩成行内大小，还靠左。只调边距，别碰 `display`。

---

## 路线 B：LaTeX 版（pandoc → xelatex）

数学排版最好、文件最小（矢量）。只在 macOS 上验证过。

```bash
pandoc /tmp/combined.md -f markdown+lists_without_preceding_blankline -t latex -s \
  --pdf-engine=xelatex -H /tmp/header.tex \
  -V documentclass=article -V geometry:"a4paper,margin=2.2cm" \
  -V CJKmainfont="Songti SC" -V monofont="Menlo" \
  -V linestretch=1.3 -V fontsize=11pt \
  -o "书名-LaTeX版.pdf" 2> /tmp/err.txt
echo "exit:$?"; grep -iE "^! |Error producing" /tmp/err.txt
grep -i "Missing character" /tmp/err.txt | sed -E 's/.*no (.+) \(U\+.*/\1/' | sort | uniq -c
```

字体说明：`Songti SC`（Songti.ttc 存在）作正文；**PingFang 在 /System/Library/Fonts 里 grep 不到，少用**；Latin Modern 自动管拉丁字母与数学。Linux 上可以试 `Noto Serif CJK SC`（`apt install fonts-noto-cjk`），Windows 上可以试 `SimSun`，这两个没实测过。用 `fc-list :lang=zh` 看本机有哪些中文字体。

`/tmp/header.tex`（缺字符号回退 + 版式微调）：

```latex
\usepackage{newunicodechar}
\newfontfamily\symfont{Apple Symbols}
\newfontfamily\boxfont{Menlo}
\newunicodechar{☼}{{\symfont\char"263C}}
\newunicodechar{→}{{\symfont\char"2192}}
\newunicodechar{↔}{{\symfont\char"2194}}
\newunicodechar{■}{{\boxfont\char"25A0}}
\newunicodechar{□}{{\boxfont\char"25A1}}
\newunicodechar{▦}{{\boxfont\char"25A6}}
\newunicodechar{┐}{{\boxfont\char"2510}}
\usepackage{titlesec}
\titleformat{\section}{\Large\bfseries\sffamily}{}{0pt}{}
\titleformat{\subsection}{\large\bfseries\sffamily}{}{0pt}{}
\setlength{\parskip}{0.4em}\setlength{\parindent}{0pt}
```

`Apple Symbols`、`Menlo` 是 macOS 自带字体。别的系统换成本机有的符号字体和等宽字体（如 `DejaVu Sans`、`DejaVu Sans Mono`）。

### LaTeX 路线四个必避的坑（都会致命或缺字）

1. **正文/标题里"字面"的 n 元算符 `∏ ∫`（U+220F/222B）→ 致命 "Missing $ inserted"。** 必须在源 md 里改成数学模式 `$\prod$` `$\int$`。newunicodechar 治不了这两个（反而会触发报错）。
2. **数学模式 `$...$` 里混进中文标点 。（）→ 落到数学字体缺字。** 要把中文（含标点）整段包进 `\text{…}`。
3. **字面 `≥ ≤` → 改 `$\ge$` `$\le$`** 走数学字体。
4. **newunicodechar 的替换文本必须用 `\char"码位`，不能再写原字符**——自引用会递归并报 Missing $。回退目标字体：符号/箭头/天文用 `Apple Symbols`，方块/制表符用 `Menlo`（macOS 通常自带）。

---

## 验收

- **路线 A**：脚本没报 "Could not convert TeX math" 就算干净。
- **路线 B**：`grep` 日志里 **`Error producing` 与 `Missing character` 都为空** 才算干净。

然后翻一遍 PDF，重点看：含特殊字符的图（如等宽方块图对齐）、公式居中与基线、难度符号 ☼ 显示是否正常、列表有没有糊成一段。本机有 poppler 的，可以 `pdftoppm -r 60 -png -f 1 -l 5 书名.pdf 页` 抽几页转成图片看；没有的话，请用户自己翻一遍。
