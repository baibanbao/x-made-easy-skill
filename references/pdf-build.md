# 把书稿合成 PDF（中文 + 数学）

两条已在 macOS 验证的路线。书里有数学公式且要排版精致 → 走 **B（LaTeX）**；只有中文、要快要稳 → 走 **A（网页）**。两本样书都用过。

依赖检查：`pandoc`、`xelatex`（B 用）、Google Chrome（A 用）。如果本机没有 poppler，**PDF 无法渲成图片肉眼校对，最后要让用户自己翻一遍**。

拼接所有分章为一份（两位数字前缀保证顺序）：

```bash
cd "/path/to/书文件夹"
: > /tmp/combined.md
first=1
for f in $(ls -1 *.md | sort); do
  # LaTeX 路线才插分页；网页路线靠 CSS h1 分页，可省下面这行
  if [ $first -eq 0 ]; then printf '\n\n```{=latex}\n\\newpage\n```\n\n' >> /tmp/combined.md; fi
  cat "$f" >> /tmp/combined.md; first=0
done
```

---

## 路线 A：网页版（pandoc → HTML+MathML → Chrome 打印）

数学走 Chrome 原生 MathML，不联网。容错最高，中文代码块、中文标点都不出问题。

```bash
pandoc /tmp/combined.md -f markdown -t html5 -s --mathml \
  -c /tmp/book.css --metadata pagetitle="书名" -o /tmp/book.html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --run-all-compositor-stages-before-draw --virtual-time-budget=15000 \
  --print-to-pdf="书名-网页版.pdf" "file:///tmp/book.html"
```

`/tmp/book.css` 关键项：正文 `"Songti SC"`，标题 `"PingFang SC"`，代码 `"Menlo"`；`h1{page-break-before:always}` 每章分页（首个 `h1:first-of-type{page-break-before:avoid}`）；`@page{size:A4;margin:20mm 18mm}`；`pre{white-space:pre-wrap}`；`math[display="block"]{text-align:center}`。

**坑**：pandoc 的 MathML 写不出 `\dbinom`/`\dfrac`（带 d 的显示版），要改用 `\binom`/`\frac`，否则原样吐出 TeX 文本。

---

## 路线 B：LaTeX 版（pandoc → xelatex）

数学排版最好、文件最小（矢量）。

```bash
pandoc /tmp/combined.md -f markdown -t latex -s \
  --pdf-engine=xelatex -H /tmp/header.tex \
  -V documentclass=article -V geometry:"a4paper,margin=2.2cm" \
  -V CJKmainfont="Songti SC" -V monofont="Menlo" \
  -V linestretch=1.3 -V fontsize=11pt \
  -o "书名-LaTeX版.pdf" 2> /tmp/err.txt
echo "exit:$?"; grep -iE "^! |Error producing" /tmp/err.txt
grep -i "Missing character" /tmp/err.txt | sed -E 's/.*no (.+) \(U\+.*/\1/' | sort | uniq -c
```

字体说明：`Songti SC`（Songti.ttc 存在）作正文；**PingFang 在 /System/Library/Fonts 里 grep 不到，少用**；Latin Modern 自动管拉丁字母与数学。

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

### LaTeX 路线四个必避的坑（都会致命或缺字）

1. **正文/标题里"字面"的 n 元算符 `∏ ∫`（U+220F/222B）→ 致命 "Missing $ inserted"。** 必须在源 md 里改成数学模式 `$\prod$` `$\int$`。newunicodechar 治不了这两个（反而会触发报错）。
2. **数学模式 `$...$` 里混进中文标点 。（）→ 落到数学字体缺字。** 要把中文（含标点）整段包进 `\text{…}`。
3. **字面 `≥ ≤` → 改 `$\ge$` `$\le$`** 走数学字体。
4. **newunicodechar 的替换文本必须用 `\char"码位`，不能再写原字符**——自引用会递归并报 Missing $。回退目标字体：符号/箭头/天文用 `Apple Symbols`，方块/制表符用 `Menlo`（macOS 通常自带）。

### 验收标准

`grep` 日志里 **`Error producing` 与 `Missing character` 都为空** 才算干净。然后请用户翻一遍 PDF，重点看：含特殊字符的图（如等宽方块图对齐）、公式居中与基线、难度符号 ☼ 显示是否正常。
