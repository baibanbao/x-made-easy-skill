#!/usr/bin/env python3
"""轻松学书稿自检：扫一个书文件夹里的分章 Markdown，查体例和语言纪律。

用法：
    python3 check_book.py 书文件夹 [--strict]

只认 NN-章名.md（两位数字前缀）。00 是目录与体例，99 是结语与附录，
01–98 是正文章，正文章要查五段式收尾。

"错"：违反铁律或体例，必须改。
"提醒"：可能有问题，逐条看，有理由就留着。
有"错"时退出码为 1；加 --strict 时"提醒"也算。只用标准库。
"""

import difflib
import re
import sys
from collections import defaultdict
from pathlib import Path

CHAPTER_RE = re.compile(r"^(\d\d)-.+\.md$")

# 铁律 3：汤普森骂的那种书的口头禅，外加几句套话。
# "易X"前面是"容"时不算（"容易得多"不是"易得"）。
BANNED = [
    "总的来说", "总而言之", "综上所述",
    "显然", "显而易见", "易知", "易证", "易得",
    "不难看出", "不难发现", "不难证明", "不难得出",
    "众所周知", "留给读者", "值得注意的是",
]
BANNED_RE = [(w, re.compile(("(?<!容)" if w.startswith("易") else "") + re.escape(w)))
             for w in BANNED]
# "显然"一家子：章名拆了其中一个，整家放过
OBVIOUS = {"显然", "显而易见", "易知", "易证", "易得",
           "不难看出", "不难发现", "不难证明", "不难得出"}
# 引号里的词是在谈论它，不是在用它
QUOTED_RE = re.compile(r"“[^”]*”|「[^」]*」|『[^』]*』|‘[^’]*’|\"[^\"]*\"")

SOURCE_TAGS = ("自编", "经典", "民间", "出处", "改编", "来源")
CJK = r"[　-〿一-鿿＀-￯]"
ASCII_BANG = re.compile(rf"(?<={CJK})!|!(?={CJK})")
# 开篇第一句报序号："第三件工具……""第二个战场是……"
ORDINAL_OPEN = re.compile(r"^(第[一二三四五六七八九十百\d]+|最后一|下一)[件个章种步招把条]")
TAKEAWAY = "这一章要带走的东西"
ENDING = "就这样。"
# 全书允许重复的句子
REPEAT_OK = {ENDING, TAKEAWAY, TAKEAWAY + "：", TAKEAWAY + ":"}


def strip_code_and_math(lines):
    """把代码块、行内代码、数学式换成空白，行号不变。"""
    out, fence = [], None
    for line in lines:
        s = line.lstrip()
        if fence:
            if s.startswith(fence):
                fence = None
            out.append("")
            continue
        if s.startswith("```") or s.startswith("~~~"):
            fence = s[:3]
            out.append("")
            continue
        line = re.sub(r"`[^`]*`", " ", line)
        line = re.sub(r"\$\$.*?\$\$", " ", line)
        line = re.sub(r"\$[^$]+\$", " ", line)
        out.append(line)
    return out


def quoted_spans(line):
    return [m.span() for m in QUOTED_RE.finditer(line.replace("*", "​"))]


def plain(line):
    """去掉 Markdown 记号，只留文字，用来比句子。"""
    line = re.sub(r"^\s*(#+|>|[-*+]|\d+\.)\s*", "", line)
    return line.replace("*", "").replace("_", "").strip()


def sentences(text_lines):
    for line in text_lines:
        for s in re.split(r"(?<=[。？；])", plain(line)):
            s = s.strip()
            if (len(re.findall(r"[一-鿿]", s)) >= 10
                    and s not in REPEAT_OK):
                yield s


def first_paragraph(text_lines):
    """标题之后的第一段正文，用来比开篇像不像。"""
    buf = []
    for line in text_lines:
        p = plain(line)
        if line.lstrip().startswith("#"):
            if buf:
                break
            continue
        if not p:
            if buf:
                break
            continue
        buf.append(p)
    return "".join(buf)


def check_file(path, is_chapter, sources_in_appendix, report):
    raw = path.read_text(encoding="utf-8").splitlines()
    text = strip_code_and_math(raw)
    # 专门拆这个词的章（如《"显然"是怎么来的》），放过章名里的词
    title = path.stem + next((l for l in text if re.match(r"#\s", l)), "")
    exempt = {w for w in BANNED if w in title}
    if exempt & OBVIOUS:
        exempt |= OBVIOUS

    for n, line in enumerate(text, 1):
        if "！" in line:
            report("错", n, "全角感叹号「！」")
        if ASCII_BANG.search(line):
            report("错", n, "感叹号「!」")
        spans = quoted_spans(line)
        for word, pattern in BANNED_RE:
            if word in exempt:
                continue
            for m in pattern.finditer(line):
                if not any(a <= m.start() < b for a, b in spans):
                    report("错", n, f"禁用词「{word}」")

    if not is_chapter:
        return text

    body = "\n".join(text)
    if TAKEAWAY not in body:
        report("错", None, f"缺「{TAKEAWAY}」小结")
    last = next((plain(l) for l in reversed(text) if plain(l)), "")
    if last != ENDING:
        report("错", None, f"最后一句应单独是「{ENDING}」，现在是「{last[:20]}」")

    h1 = [n for n, l in enumerate(text, 1) if re.match(r"#\s", l)]
    if len(h1) > 1:
        report("提醒", h1[1], "一章出现多个一级标题，是不是塞了两个概念")

    examples = [n for n, l in enumerate(text, 1) if "☼" in l]
    if not sources_in_appendix:
        for n in examples:
            nearby = "".join(text[n - 1:n + 2])
            if not any(tag in nearby for tag in SOURCE_TAGS):
                report("提醒", n, "例子没标出处（自编/经典/民间），附录里也没有出处说明")
    return text


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    strict = "--strict" in argv
    if len(args) != 1:
        print(__doc__.strip())
        return 2
    book = Path(args[0])
    if not book.is_dir():
        print(f"不是文件夹：{book}")
        return 2

    files = sorted(p for p in book.glob("*.md") if CHAPTER_RE.match(p.name))
    others = sorted(p.name for p in book.glob("*.md") if not CHAPTER_RE.match(p.name))
    if not files:
        print(f"没找到 NN-章名.md 形式的文件：{book}")
        return 2

    problems = defaultdict(list)
    general = []

    def reporter(name):
        def report(level, line, msg):
            where = f"第 {line} 行：" if line else ""
            problems[name].append((level, where + msg))
        return report

    prefixes = {CHAPTER_RE.match(p.name).group(1) for p in files}
    if "00" not in prefixes:
        general.append(("提醒", "还没有 00-目录与体例.md"))
    if "99" not in prefixes:
        general.append(("提醒", "还没有 99-结语与附录.md（写完正文再补）"))
    for name in others:
        general.append(("提醒", f"{name} 没有两位数字前缀，自检和合成 PDF 都会跳过它"))

    appendix = next((p for p in files if p.name.startswith("99-")), None)
    sources_in_appendix = bool(appendix) and "出处" in appendix.read_text(encoding="utf-8")

    chapters = {}
    for p in files:
        is_chapter = CHAPTER_RE.match(p.name).group(1) not in ("00", "99")
        text = check_file(p, is_chapter, sources_in_appendix, reporter(p.name))
        if is_chapter:
            chapters[p.name] = text

    suns = {n: sum("☼" in l for l in t) for n, t in chapters.items()}
    if chapters and not any(suns.values()):
        general.append(("提醒", "全书没用难度标注 ☼。非解题类主题可以不用，但要在 00 里说明"))
    else:
        for n, count in suns.items():
            if count < 2:
                problems[n].append(("提醒", f"标了难度的例子只有 {count} 个，每章至少两个"))

    # 同一句话在三章以上出现
    seen = defaultdict(set)
    for name, text in chapters.items():
        for s in sentences(text):
            seen[s].add(name)
    for s, names in seen.items():
        if len(names) >= 3:
            general.append(("提醒", f"这句在 {len(names)} 章里重复：「{s[:30]}」"))

    # 开篇报序号：报的是目录，不是恐惧
    names = list(chapters)
    openings = {n: first_paragraph(chapters[n]) for n in names}
    ordinal = [n for n in names if ORDINAL_OPEN.match(openings[n])]
    if len(ordinal) >= 3:
        general.append(("提醒", f"{len(ordinal)} 章用序号开篇（"
                        + "、".join(n[:2] for n in ordinal)
                        + "）。序号报的是目录，不是恐惧，挪到第二句"))

    # 开篇和前面某章太像
    for i, a in enumerate(names):
        for b in names[:i]:
            if openings[a] and openings[b]:
                r = difflib.SequenceMatcher(None, openings[a], openings[b]).ratio()
                if r >= 0.6:
                    problems[a].append(("提醒", f"开篇和 {b} 太像（相似度 {r:.0%}），换个切口"))

    errors = warnings = 0
    for level, msg in general:
        print(f"{level:　<2} {msg}")
    for p in files:
        items = problems.get(p.name)
        if not items:
            continue
        print(f"\n{p.name}")
        for level, msg in items:
            print(f"  {level:　<2} {msg}")
    for level, _ in general + [i for v in problems.values() for i in v]:
        if level == "错":
            errors += 1
        else:
            warnings += 1

    print(f"\n共 {len(files)} 个文件，{errors} 处错，{warnings} 处提醒。")
    return 1 if errors or (strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
