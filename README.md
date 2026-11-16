# Hytale protocol docs

Published at <https://mastercake10.github.io/hytale_proto>.

Markdown in `docs/`, one script, static HTML in `site/`. No dependencies
besides Python 3, no JavaScript in the output.

```sh
python3 build.py                        # docs/*.md -> site/*.html
python3 -m http.server -d site 8080     # preview
```

`site/` is plain files, so any web server can host it. With podman:

```sh
podman run -d --name protocol-docs -p 127.0.0.1:8080:80 \
  -v "$PWD/site:/usr/share/caddy:ro,Z" docker.io/library/caddy
```

## GitHub Pages

`.github/workflows/pages.yml` builds and deploys on every push to `main`.
Once, in the repository: Settings -> Pages -> Source: "GitHub Actions".
`site/` is ignored by git; the workflow builds it.

## Pages

`docs/index.md` is the front page; its `# title` is the site title. Other
pages are named by their numeric prefix: `03-movement.md` becomes
`movement.html`. The packet index is generated.

The sidebar comes from `NAV` in `build.py`: four groups (Start, Player, World,
Reference) with short labels. Every page must be listed there; the build fails
otherwise. Add a page by adding its name and label to `NAV`.
`docs/_footer.md` is the notice shown at the bottom of every page.

`style.css` follows the browser: light by default, dark when it prefers dark.

## Packet definitions

A heading of the form `## Name (ID)` starts a packet. The `packet` block
below it holds the rest:

````
## SetActiveSlot (177)

Free text.

```packet
bound: client
summary: Active hotbar slot correction/update
`inventory_section_id` | `i32` | `-1` in a correction from the server
`active_slot`          | `i32`
```
````

- `bound`: `client`, `server`, `both` or `?` (who receives it)
- `summary`: one line for the packet index
- `partial: yes`: adds the caption "Known fields (incomplete, order not confirmed)"
- `fields: none`: the packet is known to have no fields
- field lines: `name | type | notes`, notes optional
- `columns: Offset | Field Name | Field Type | Notes`: use other columns than the
  default three; field lines then follow that order
- no field lines: the table says "not documented"

Packets without a section of their own go into a list:

````
```packets
3 | Ping | both | Keepalive
4 | Pong | both | Keepalive reply
```
````

## Links

- `[[SetColumn]]` links to wherever that packet is defined.
- `[text](01-framing.md#data-types)` links to a page or section; anchors are
  the heading in lower case with spaces as `-`.
- `[text](packets.md)` links to the generated packet index.

## What the build checks

The build fails with file and line on: unknown `[[Packet]]`, links to missing
pages or sections, duplicate packet ids or names, a packet heading without a
block, malformed field lines, and table rows with the wrong number of cells.

## Supported Markdown

Headings, paragraphs, one-level `-` and `1.` lists, fenced code, pipe tables
(with `:--`/`--:` alignment), `code`, `**bold**`, `*italic*`, links. No
nested lists, images, block quotes or raw HTML; add them to `build.py` when
needed.
