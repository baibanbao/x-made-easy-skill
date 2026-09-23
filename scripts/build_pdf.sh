#!/usr/bin/env bash
# 把一个轻松学书文件夹合成 PDF（网页路线：pandoc → HTML+MathML → Chrome/Chromium 打印）。
#
# 用法：scripts/build_pdf.sh 书文件夹 [书名]
#   书名缺省用文件夹名；PDF 写到 书文件夹/书名.pdf。
#
# 依赖：pandoc；Chrome、Chromium、Edge 三者之一。浏览器找不到时，
#   用环境变量 CHROME 指定：CHROME=/path/to/chrome scripts/build_pdf.sh ...
# 要 LaTeX 精排，见 references/pdf-build.md 路线 B。
set -euo pipefail

book_dir=${1:?用法：build_pdf.sh 书文件夹 [书名]}
book_dir=$(cd "$book_dir" && pwd)
title=${2:-$(basename "$book_dir")}
here=$(cd "$(dirname "$0")" && pwd)
out="$book_dir/$title.pdf"

command -v pandoc >/dev/null || { echo "缺 pandoc：macOS 用 brew install pandoc，Debian/Ubuntu 用 apt install pandoc" >&2; exit 1; }

find_chrome() {
  if [[ -n "${CHROME:-}" ]]; then echo "$CHROME"; return; fi
  local c
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"; do
    [[ -x "$c" ]] && { echo "$c"; return; }
  done
  for c in google-chrome google-chrome-stable chromium chromium-browser microsoft-edge; do
    command -v "$c" >/dev/null && { command -v "$c"; return; }
  done
  return 1
}
chrome=$(find_chrome) || { echo "找不到 Chrome/Chromium/Edge，用 CHROME=浏览器路径 指定" >&2; exit 1; }

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# 只认 NN-章名.md；两位数字前缀保证顺序，C 排序不受系统语言影响
export LC_ALL=C
shopt -s nullglob
files=("$book_dir"/[0-9][0-9]-*.md)
(( ${#files[@]} )) || { echo "没找到 NN-章名.md 形式的分章文件：$book_dir" >&2; exit 1; }

# 章与章之间空两行，免得下一章标题粘在上一章末尾
for f in "${files[@]}"; do cat "$f"; printf '\n\n'; done > "$work/combined.md"

# 图片按书文件夹找，样式和图片都嵌进一个 HTML。
# 列表、引用块前面没空行也认：模型写的稿子常这样，默认读法会把列表糊成一段。
embed=--embed-resources
[[ $(pandoc --help) == *--embed-resources* ]] || embed=--self-contained
reader=markdown+lists_without_preceding_blankline-blank_before_blockquote
pandoc "$work/combined.md" -f "$reader" -t html5 -s --mathml "$embed" \
  --resource-path="$book_dir" -c "$here/book.css" \
  --metadata pagetitle="$title" -o "$work/book.html" 2> "$work/pandoc.log" || {
  cat "$work/pandoc.log" >&2; exit 1; }
# pandoc 转不动的公式会原样吐出 TeX，提示出来
grep -A2 "Could not convert TeX math" "$work/pandoc.log" >&2 || true

flags=(--headless=new --disable-gpu --no-pdf-header-footer
       --run-all-compositor-stages-before-draw --virtual-time-budget=15000)
[[ $(uname) == Linux && $(id -u) == 0 ]] && flags+=(--no-sandbox)
"$chrome" "${flags[@]}" --print-to-pdf="$out" "file://$work/book.html" 2> "$work/chrome.log" || {
  cat "$work/chrome.log" >&2; exit 1; }

[[ -s "$out" ]] || { echo "PDF 没生成：" >&2; cat "$work/chrome.log" >&2; exit 1; }
echo "已生成：$out（${#files[@]} 个文件）"
