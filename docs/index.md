# Hytale Protocol

Reference for the Hytale network protocol: packet layouts and the server
behaviour tied to them, for implementing a client, server or other
protocol-speaking software. Undocumented parts are marked `?`.

## Pages

- [Packet framing and streams](01-framing.md)
- [Authentication flow](02-auth.md)
- [Movement and timing](03-movement.md)
- [Interaction chains](04-interactions.md)
- [World and chunk data](05-world-chunks.md)
- [Interface and page packets](06-interface-pages.md)
- [Inventory and active slots](07-inventory-slots.md)
- [Protocol glossary](08-glossary.md)
- [Other packets](09-other-packets.md)
- [Markers and overlays](10-marker-overlays.md)
- [Spawn points and position recall](11-spawn-and-recall.md)

## Conventions

- Numbers are little-endian; packet IDs are decimal.
- Field types: [Data types](01-framing.md#data-types).
- **Bound** names the receiver: `server` = sent by the client, `client` = sent
  by the server, `both` = either way.
- `code` names are wire identifiers; plain names are descriptions.
- `@N` / offset columns are byte offsets from the start of the struct.
- Variable-block offsets are `i32`, relative to the variable block start,
  `-1` = absent.
- A packet table without a caption lists all fields in wire order. "Known
  fields" tables are partial and unordered.
