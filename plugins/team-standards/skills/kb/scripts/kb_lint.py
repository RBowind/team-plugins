#!/usr/bin/env python3
"""kb_lint —— 团队知识库的机械检查。

只做能确定判断的检查，语义判断（内容是否仍与代码一致、两条知识是否真重复）
交给人和 kb-reviewer。输出候选名单，不修改任何文件。

用法:
    python kb_lint.py --root docs/kb
    python kb_lint.py --root docs/kb --json
    python kb_lint.py --root docs/kb --strict --max-age-days 120

退出码: 有 error → 1；只有 warning → 0（--strict 时 → 1）；干净 → 0。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

KINDS = {"flow", "entity", "service", "integration", "decision"}
KIND_DIRS = {k: k + "s" for k in KINDS}
KIND_DIRS["entity"] = "entities"
STATUSES = {"draft", "review", "stable"}
REQUIRED = ("title", "kind", "status", "owner", "services", "verified_at")
SKIP_DIRS = {".git", ".obsidian", "node_modules", "__pycache__", ".venv", "dist", "build"}
FENCE = re.compile(r"^\s*(```|~~~)")
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEADING = re.compile(r"^#{1,6}\s+(.*)$")


class Finding:
    def __init__(self, level: str, code: str, path: Path, line: int, message: str):
        self.level = level
        self.code = code
        self.path = path
        self.line = line
        self.message = message

    def as_dict(self, root: Path) -> dict:
        return {
            "level": self.level,
            "code": self.code,
            "file": rel(self.path, root),
            "line": self.line,
            "message": self.message,
        }


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def strip_fences(text: str) -> str:
    """把围栏代码块内容置空，行号保持不变，避免把示例链接当真实链接。"""
    out, inside = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            inside = not inside
            out.append("")
            continue
        out.append("" if inside else line)
    return "\n".join(out)


def parse_frontmatter(text: str):
    """返回 (fields, body_start_line)。无 frontmatter 时返回 (None, 1)。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, 1
    fields: dict[str, object] = {}
    current_key = None
    for i, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return fields, i + 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(("  ", "\t")) and current_key:
            item = line.strip().lstrip("-").strip()
            if item:
                fields.setdefault(current_key, [])
                if isinstance(fields[current_key], list):
                    fields[current_key].append(item)
            continue
        if ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key, raw = key.strip(), raw.strip()
        current_key = key
        if raw.startswith("[") and raw.endswith("]"):
            fields[key] = [x.strip().strip("\"'") for x in raw[1:-1].split(",") if x.strip()]
        elif raw:
            fields[key] = raw.strip("\"'")
        else:
            fields[key] = []
    return None, 1  # 没有闭合的 --- 视为无 frontmatter


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"[\s\W_]+", "", text)


def bigrams(text: str) -> set[str]:
    n = normalize(text)
    if len(n) < 2:
        return {n} if n else set()
    return {n[i : i + 2] for i in range(len(n) - 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def collect_links(md: Path, root: Path):
    """返回 [(行号, 目标路径, 原文)]，只收相对链接。"""
    text = md.read_text(encoding="utf-8", errors="replace")
    body = strip_fences(text)
    out = []
    for lineno, line in enumerate(body.splitlines(), start=1):
        for _, target in LINK.findall(line):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not clean:
                continue
            out.append((lineno, (md.parent / clean).resolve(), target))
    return out


def lint(root: Path, max_age_days: int, draft_age_days: int):
    findings: list[Finding] = []
    pages: list[Path] = []
    index_file = root / "index.md"

    for md in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in md.parts):
            continue
        if md.name == "index.md" and md.parent == root:
            continue
        pages.append(md)

    # 链接与断链（index.md 也参与，导航里的断链同样要报）
    link_files = pages + ([index_file] if index_file.exists() else [])
    inbound: dict[Path, set[Path]] = {p.resolve(): set() for p in pages}
    for md in link_files:
        for lineno, target, raw in collect_links(md, root):
            if target in inbound and target != md.resolve():
                inbound[target].add(md.resolve())
            if not target.exists():
                findings.append(Finding("error", "E4", md, lineno, f"断链：{raw} 指向的文件不存在"))

    index_text = index_file.read_text(encoding="utf-8", errors="replace") if index_file.exists() else ""
    index_links = {t for _, t, _ in collect_links(index_file, root)} if index_file.exists() else set()
    if not index_file.exists():
        findings.append(Finding("error", "E5", root / "index.md", 0, "缺 index.md：知识库需要一份导航"))

    today = dt.date.today()
    titles: dict[str, Path] = {}
    metas: dict[Path, dict] = {}

    for md in pages:
        text = md.read_text(encoding="utf-8", errors="replace")
        fields, body_start = parse_frontmatter(text)

        if fields is None:
            findings.append(Finding("error", "E1", md, 1, "缺 frontmatter 或未闭合（以 --- 开头并以 --- 结束）"))
            continue

        for key in REQUIRED:
            value = fields.get(key)
            if value in (None, "", []):
                findings.append(Finding("error", "E2", md, 1, f"frontmatter 缺 {key}"))

        kind = str(fields.get("kind", ""))
        if kind and kind not in KINDS:
            findings.append(Finding("error", "E3", md, 1, f"kind 取值非法：{kind}（合法值 {'/'.join(sorted(KINDS))}）"))
        elif kind and KIND_DIRS[kind] != md.parent.name:
            findings.append(Finding("warning", "W6", md, 1, f"kind={kind} 与所在目录 {md.parent.name}/ 不一致"))

        status = str(fields.get("status", ""))
        if status and status not in STATUSES:
            findings.append(Finding("error", "E3", md, 1, f"status 取值非法：{status}（合法值 draft/review/stable）"))

        verified = str(fields.get("verified_at", ""))
        age = None
        if verified:
            if not DATE.match(verified):
                findings.append(Finding("error", "E3", md, 1, f"verified_at 格式非法：{verified}（要求 YYYY-MM-DD）"))
            else:
                age = (today - dt.date.fromisoformat(verified)).days
                limit = max_age_days if status == "stable" else draft_age_days
                if age > limit:
                    label = "稳定页超过复核期" if status == "stable" else "未定档页面停留过久"
                    findings.append(
                        Finding("warning", "W2", md, 1, f"{label}：verified_at={verified}（{age} 天 > {limit} 天）")
                    )

        body = text.splitlines()[body_start - 1 :] if body_start > 1 else text.splitlines()
        body_text = "\n".join(body)
        if not re.search(r"^##\s+证据\s*$", body_text, re.MULTILINE):
            findings.append(Finding("warning", "W3", md, body_start, "缺「## 证据」段：页面需要标明证据来源"))

        title = str(fields.get("title", "")) or md.stem
        summary = " ".join(
            line.strip() for line in body_text.splitlines()[:6] if line.strip() and not HEADING.match(line)
        )[:200]
        metas[md] = {
            "title": title,
            "summary": summary,
            "kind": kind,
            "status": status,
            "age": age,
            "inbound": inbound.get(md.resolve(), set()),
        }
        if title in titles:
            findings.append(Finding("warning", "W4", md, 1, f"标题与 {rel(titles[title], root)} 相同，疑重复归属"))
        else:
            titles[title] = md

        if not inbound.get(md.resolve()) and md.resolve() not in index_links:
            findings.append(Finding("warning", "W1", md, 1, "孤立页：没有入链，也没进 index.md"))

    # 疑似重复：标题加首段摘要的字符二元组重合度超阈值，或一个标题包含另一个，只列候选
    pairs = []
    items = list(metas.items())
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a_meta, b_meta = metas[items[i][0]], metas[items[j][0]]
            score = jaccard(
                bigrams(a_meta["title"] + a_meta["summary"]), bigrams(b_meta["title"] + b_meta["summary"])
            )
            short, long = sorted((normalize(a_meta["title"]), normalize(b_meta["title"])), key=len)
            contained = len(short) >= 4 and short in long
            if score >= 0.35 or contained:
                reason = "标题互相包含" if contained and score < 0.35 else f"标题与摘要重合 {score:.2f}"
                pairs.append((score, items[i][0], items[j][0], reason))
    for _, a, b, reason in sorted(pairs, reverse=True)[:10]:
        findings.append(
            Finding("warning", "W4", b, 1, f"与 {rel(a, root)} {reason}，疑重复解释同一事实")
        )

    findings.sort(key=lambda f: (f.level != "error", f.code, rel(f.path, root), f.line))
    return findings, pages, metas


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass

    parser = argparse.ArgumentParser(description="团队知识库机械检查")
    parser.add_argument("--root", required=True, help="知识库根目录，如 docs/kb")
    parser.add_argument("--max-age-days", type=int, default=180, help="稳定页复核期（默认 180 天）")
    parser.add_argument("--draft-age-days", type=int, default=90, help="draft/review 页停留上限（默认 90 天）")
    parser.add_argument("--json", action="store_true", help="输出 JSON，便于别的工具消费")
    parser.add_argument("--strict", action="store_true", help="有 warning 也返回非零")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"找不到知识库根目录：{root}", file=sys.stderr)
        return 2

    findings, pages, metas = lint(root, args.max_age_days, args.draft_age_days)
    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]

    if args.json:
        print(
            json.dumps(
                {
                    "root": root.as_posix(),
                    "pages": len(pages),
                    "errors": len(errors),
                    "warnings": len(warnings),
                    "findings": [f.as_dict(root) for f in findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"知识库 {root.as_posix()}：{len(pages)} 个页面，{len(errors)} 个 error，{len(warnings)} 个 warning")
        for level, group, title in (("error", errors, "ERROR（必须处理）"), ("warning", warnings, "WARNING（候选名单，需人判）")):
            if not group:
                continue
            print(f"\n{title}")
            for f in group:
                loc = f"{rel(f.path, root)}:{f.line}" if f.line else rel(f.path, root)
                print(f"  [{f.code}] {loc}  {f.message}")
        if not findings:
            print("检查通过。")

    if errors:
        return 1
    return 1 if args.strict and warnings else 0


if __name__ == "__main__":
    sys.exit(main())