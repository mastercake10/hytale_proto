#!/usr/bin/env python3
"""Build the protocol docs: docs/*.md -> site/*.html. Standard library only.

Supported Markdown: # headings, paragraphs, - and 1. lists (one level),
fenced code, pipe tables, `code`, **bold**, *italic*, [text](url).
Extensions: ```packet / ```packets blocks and [[PacketName]] links.
See README.md for the block syntax.
"""
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC, OUT = ROOT / "docs", ROOT / "site"
BOUND = {"client": "Client", "server": "Server", "both": "Both", "?": "?"}

errors = []
packets = {}  # name -> {id, name, bound, summary, page, anchor}


def fail(page, msg):
    errors.append(f"{page.src.name}: {msg}")


def slug(text):
    text = re.sub(r"[^\w\s-]", "", text.replace("`", "").lower())
    return re.sub(r"\s+", "-", text.strip())


def split_cells(line):
    """Split a table row on | while leaving `code spans` and \\| alone."""
    cells, cur, in_code, i = [], "", False, 0
    line = line.strip()
    while i < len(line):
        c = line[i]
        if c == "\\" and line[i + 1 : i + 2] == "|":
            cur, i = cur + "|", i + 1
        elif c == "`":
            in_code, cur = not in_code, cur + c
        elif c == "|" and not in_code:
            cells.append(cur.strip())
            cur = ""
        else:
            cur += c
        i += 1
    cells.append(cur.strip())
    if line.startswith("|"):
        cells = cells[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        cells = cells[:-1]
    return cells


class Page:
    def __init__(self, src):
        self.src = src
        self.name = re.sub(r"^\d+-", "", src.stem)
        self.out = self.name + ".html"
        self.title = self.name
        self.blocks, self.sections, self.anchors, self.links = [], [], set(), []

    def anchor(self, a):
        if a in self.anchors:
            fail(self, f"duplicate anchor #{a}")
        self.anchors.add(a)

    # ---- block parsing -------------------------------------------------

    def parse(self):
        lines = self.src.read_text(encoding="utf-8").splitlines()
        i, current = 0, None  # current = packet opened by the last heading
        is_item = lambda s: re.match(r"^\s*([-*]|\d+\.)\s+\S", s)
        is_sep = lambda s: re.match(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$", s)
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue

            m = re.match(r"^(`{3,})\s*(\S*)\s*$", line)
            if m:
                fence, lang, body, start = m.group(1), m.group(2), [], i + 1
                i += 1
                while i < len(lines) and not re.match(rf"^`{{{len(fence)},}}\s*$", lines[i]):
                    body.append(lines[i])
                    i += 1
                if i == len(lines):
                    fail(self, f"line {start}: code fence is never closed")
                i += 1
                if lang == "packet":
                    if current is None:
                        fail(self, f"line {start}: packet block without a 'Name (ID)' heading above it")
                    else:
                        self.packet_block(body, current, start)
                        self.blocks.append(("packet", current))
                        current = None
                elif lang == "packets":
                    self.blocks.append(("packets", self.packets_block(body, start)))
                else:
                    self.blocks.append(("code", "\n".join(body)))
                continue

            m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
            if m:
                level, text = len(m.group(1)), m.group(2)
                a = slug(text)
                self.anchor(a)
                if level == 1:
                    self.title = text
                elif level == 2:
                    self.sections.append((text, a))
                if current is not None:
                    fail(self, f"packet {current['name']} has no packet block")
                pm = re.match(r"^(\w+) \((\d+)\)$", text)
                current = self.register(pm.group(1), int(pm.group(2)), a) if pm else None
                self.blocks.append(("h", level, text, a))
                i += 1
                continue

            if line.lstrip().startswith("|") and i + 1 < len(lines) and is_sep(lines[i + 1]):
                head = split_cells(line)
                align = [
                    "right" if c.endswith(":") and not c.startswith(":") else
                    "center" if c.endswith(":") else ""
                    for c in split_cells(lines[i + 1])
                ]
                rows, i = [], i + 2
                while i < len(lines) and lines[i].lstrip().startswith("|"):
                    row = split_cells(lines[i])
                    if len(row) != len(head):
                        fail(self, f"line {i + 1}: table row has {len(row)} cells, header has {len(head)}")
                    rows.append(row)
                    i += 1
                self.blocks.append(("table", head, align, rows))
                continue

            if is_item(line):
                ordered, items = bool(re.match(r"^\s*\d+\.", line)), []
                while i < len(lines) and lines[i].strip():
                    if is_item(lines[i]):
                        items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]))
                    elif lines[i].startswith(" "):
                        items[-1] += " " + lines[i].strip()
                    else:
                        break
                    i += 1
                self.blocks.append(("ol" if ordered else "ul", items))
                continue

            para, i = [line.strip()], i + 1
            while i < len(lines) and lines[i].strip() and not (
                re.match(r"^(`{3,}|#{1,6}\s)", lines[i]) or is_item(lines[i])
                or (lines[i].lstrip().startswith("|") and i + 1 < len(lines) and is_sep(lines[i + 1]))
            ):
                para.append(lines[i].strip())
                i += 1
            self.blocks.append(("p", " ".join(para)))
        if current is not None:
            fail(self, f"packet {current['name']} has no packet block")

    def register(self, name, pid, anchor):
        pk = {"id": pid, "name": name, "bound": "?", "summary": "", "page": self,
              "anchor": anchor, "fields": [], "partial": False, "nofields": False,
              "columns": ["Field Name", "Field Type", "Notes"]}
        if name in packets:
            fail(self, f"packet {name} is defined twice")
        if any(p["id"] == pid for p in packets.values()):
            fail(self, f"packet id {pid} is used twice")
        packets[name] = pk
        return pk

    def packet_block(self, body, pk, start):
        for n, ln in enumerate(body, start + 1):
            if not ln.strip():
                continue
            if "|" in ln and not ln.startswith("columns:"):
                cells = split_cells(ln)
                cols = len(pk["columns"])
                if len(cells) > cols:
                    fail(self, f"line {n}: {len(cells)} cells, but the packet has {cols} columns")
                pk["fields"].append((cells + [""] * cols)[:cols])
                continue
            m = re.match(r"^(\w+):\s*(.*)$", ln)
            key, val = m.groups() if m else ("", "")
            if key == "bound" and val in BOUND:
                pk["bound"] = val
            elif key == "summary":
                pk["summary"] = val
            elif key == "partial" and val in ("yes", "no"):
                pk["partial"] = val == "yes"
            elif key == "columns" and not pk["fields"]:
                pk["columns"] = split_cells(val)
                continue
            elif key == "fields" and val == "none":
                pk["nofields"] = True
            else:
                fail(self, f"line {n}: cannot read '{ln.strip()}'")
        if not pk["summary"]:
            fail(self, f"line {start}: packet {pk['name']} needs a summary")

    def packets_block(self, body, start):
        rows = []
        for n, ln in enumerate(body, start + 1):
            if not ln.strip():
                continue
            cells = split_cells(ln)
            if len(cells) != 4 or not cells[0].isdigit() or cells[2] not in BOUND:
                fail(self, f"line {n}: expected 'id | Name | client/server/both/? | summary'")
                continue
            a = slug(cells[1])
            self.anchor(a)
            pk = self.register(cells[1], int(cells[0]), a)
            pk.update(bound=cells[2], summary=cells[3])
            rows.append(pk)
        return rows

    # ---- rendering -----------------------------------------------------

    def link(self, text, url):
        if re.match(r"^[a-z]+:", url):
            return f'<a href="{url}">{text}</a>'
        path, _, frag = url.partition("#")
        target = self if not path else by_src.get(Path(path).name)
        if target is None:
            fail(self, f"link to unknown page '{path}'")
            return text
        self.links.append((target, frag))
        href = ("" if target is self else target.out) + (f"#{frag}" if frag else "")
        return f'<a href="{href}">{text}</a>'

    def packet_link(self, name):
        pk = packets.get(name)
        if pk is None:
            fail(self, f"[[{name}]] is not a known packet")
            return name
        href = ("" if pk["page"] is self else pk["page"].out) + "#" + pk["anchor"]
        return f'<a href="{href}">{name}</a>'

    def inline(self, text):
        out = []
        for k, part in enumerate(re.split(r"(`[^`]+`)", text)):
            if k % 2:
                out.append(f"<code>{html.escape(part[1:-1])}</code>")
                continue
            part = html.escape(part, quote=False)
            part = re.sub(r"\[\[(\w+)\]\]", lambda m: self.packet_link(m.group(1)), part)
            part = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: self.link(m.group(1), m.group(2)), part)
            part = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", part)
            part = re.sub(r"(?<![\w*])\*(?!\s)([^*]+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", part)
            out.append(part)
        return "".join(out)

    def packet_table(self, pk):
        f = self.inline
        fields, cols = pk["fields"], pk["columns"]
        cls = [' class="right"' if c == "Offset" else "" for c in cols]
        if fields:
            rows = ["".join(f"<td{cls[j]}>{f(c)}</td>" for j, c in enumerate(r)) for r in fields]
        else:
            rows = [f'<td colspan="{len(cols)}"><em>{"no fields" if pk["nofields"] else "not documented"}</em></td>']
        span = f' rowspan="{len(rows)}"' if len(rows) > 1 else ""
        rows[0] = f'<td{span}>{pk["id"]}</td><td{span}>{BOUND[pk["bound"]]}</td>' + rows[0]
        cap = "<caption>Known fields (incomplete, order not confirmed)</caption>\n" if pk["partial"] else ""
        head = "<tr><th>Packet ID</th><th>Bound To</th>" + "".join(f"<th{cls[j]}>{f(c)}</th>" for j, c in enumerate(cols)) + "</tr>"
        return f'<table class="packet">\n{cap}{head}\n' + "\n".join(f"<tr>{r}</tr>" for r in rows) + "\n</table>"

    def body(self):
        f, out = self.inline, []
        for b in self.blocks:
            kind = b[0]
            if kind == "h":
                out.append(f'<h{b[1]} id="{b[3]}">{f(b[2])}</h{b[1]}>')
            elif kind == "p":
                out.append(f"<p>{f(b[1])}</p>")
            elif kind in ("ul", "ol"):
                out.append(f"<{kind}>\n" + "\n".join(f"<li>{f(x)}</li>" for x in b[1]) + f"\n</{kind}>")
            elif kind == "code":
                out.append(f"<pre>{html.escape(b[1])}</pre>")
            elif kind == "table":
                cls = lambda j: f' class="{b[2][j]}"' if j < len(b[2]) and b[2][j] else ""
                rows = ["<tr>" + "".join(f"<th{cls(j)}>{f(c)}</th>" for j, c in enumerate(b[1])) + "</tr>"]
                rows += ["<tr>" + "".join(f"<td{cls(j)}>{f(c)}</td>" for j, c in enumerate(r)) + "</tr>" for r in b[3]]
                out.append("<table>\n" + "\n".join(rows) + "\n</table>")
            elif kind == "packet":
                out.append(self.packet_table(b[1]))
            elif kind == "packets":
                rows = ["<tr><th>Packet ID</th><th>Name</th><th>Bound To</th><th>Notes</th></tr>"]
                rows += [
                    f'<tr id="{p["anchor"]}"><td>{p["id"]}</td><td>{p["name"]}</td>'
                    f'<td>{BOUND[p["bound"]]}</td><td>{f(p["summary"])}</td></tr>'
                    for p in b[1]
                ]
                out.append('<table class="packet">\n' + "\n".join(rows) + "\n</table>")
        return "\n".join(out)


def index_body(page):
    rows = ['<tr><th class="right">ID</th><th>Name</th><th>Bound To</th><th>Summary</th></tr>']
    for p in sorted(packets.values(), key=lambda p: p["id"]):
        rows.append(
            f'<tr><td class="right">{p["id"]}</td>'
            f'<td><a href="{p["page"].out}#{p["anchor"]}">{p["name"]}</a></td>'
            f'<td>{BOUND[p["bound"]]}</td><td>{page.inline(p["summary"])}</td></tr>'
        )
    return (
        '<h1 id="packet-index">Packet index</h1>\n'
        f"<p>Generated from the packet definitions on the other pages. {len(packets)} packets.</p>\n"
        "<table>\n" + "\n".join(rows) + "\n</table>"
    )


def render(page, body, site, nav_pages, footer):
    items = []
    for p in nav_pages:
        here = p is page
        sub = ""
        if here and p.sections:
            sub = "<ul>" + "".join(f'<li><a href="#{a}">{page.inline(t)}</a></li>' for t, a in p.sections) + "</ul>"
        cls = ' class="here"' if here else ""
        items.append(f'<li{cls}><a href="{p.out}">{html.escape(p.navtitle)}</a>{sub}</li>')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page.title)} - {html.escape(site)}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header><a href="index.html">{html.escape(site)}</a></header>
<div id="wrap">
<nav>
<ul>
{chr(10).join(items)}
</ul>
</nav>
<main>
{body}
</main>
</div>
<footer>{footer}</footer>
</body>
</html>
"""


by_src = {}


def main():
    pages = [Page(p) for p in sorted(SRC.glob("[!_]*.md"), key=lambda p: (p.stem != "index", p.name))]
    if not pages or pages[0].name != "index":
        sys.exit("docs/index.md is missing")
    for p in pages:
        if p.name == "packets" or any(q is not p and q.name == p.name for q in pages):
            errors.append(f"{p.src.name}: page name '{p.name}' is taken")
        by_src[p.src.name] = p
        p.parse()
        p.navtitle = p.title
    site = pages[0].title
    pages[0].navtitle = "Overview"

    index = Page(SRC / "packets.md")
    index.title = index.navtitle = "Packet index"
    by_src["packets.md"] = index  # lets pages link to the generated index
    nav = [pages[0], index] + pages[1:]

    rendered = [(p, p.body()) for p in pages] + [(index, index_body(index))]
    note = SRC / "_footer.md"
    footer = pages[0].inline(" ".join(note.read_text(encoding="utf-8").split())) if note.exists() else ""
    for p in pages:
        for target, frag in p.links:
            if frag and frag not in target.anchors:
                fail(p, f"link to missing section {target.src.name}#{frag}")
    if errors:
        sys.exit("\n".join(["build failed:"] + sorted(set(errors))))

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for p, body in rendered:
        (OUT / p.out).write_text(render(p, body, site, nav, footer), encoding="utf-8")
    shutil.copy(ROOT / "style.css", OUT / "style.css")
    print(f"{len(pages)} pages, {len(packets)} packets -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
