# Hytale Protocol

Working notes on the Hytale network protocol: packet structure and the server
behavior that comes with it. The aim is to cover what is needed to write a
client, a server or other software that speaks the protocol.

This is not an operational guide. It intentionally contains no step-by-step
client-modification instructions, no credentials, and no account data.

The notes are incomplete. Gaps are marked with `?` instead of being guessed.

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

## Conventions

- All numeric fields are little-endian unless noted.
- Field types are listed under [Data types](01-framing.md#data-types).
- Packet IDs are decimal.
- **Bound To** names the receiver: `Server` is sent by the client, `Client` is
  sent by the server, `Both` goes either way.
- Field names in `code` are identifiers; plain names are descriptions.
- `?` in a table means the type or layout is not documented yet.
- A packet table without a caption lists all fields in wire order. A table
  captioned "Known fields" is partial and its order is not confirmed.
