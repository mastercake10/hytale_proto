# Packet Framing and Streams

Transport is QUIC. Packets are framed inside QUIC streams.

## Frame format

| Field Name       | Field Type             | Notes                                       |
|------------------|------------------------|---------------------------------------------|
| `payload_length` | `u32` LE               | Body length only (compressed size if compressed) |
| `packet_id`      | `u32` LE               | See [Packet IDs](packets.md)                |
| `payload`        | `payload_length` bytes | Packet body                                 |

The server closes the connection (QUIC `PROTOCOL_VIOLATION`) when:

- `payload_length` is negative or above 1 677 721 600,
- `packet_id` is not a known client-to-server packet,
- `payload_length` exceeds the packet's maximum size,
- the packet arrives on a stream other than its assigned channel,
- the body fails to decode.

## Streams

| Channel | Value | Stream | Packets |
|---------|-------|--------|---------|
| Default  | 0 | Main bidirectional stream, opened by the client | Everything not listed below |
| Chunks   | 1 | Unidirectional, opened by the server | Chunk, column, block, fluid, heightmap and unload packets, e.g. [[SetChunk]], [[SetColumn]] |
| WorldMap | 2 | Unidirectional, opened by the server | `UpdateWorldMap`, `ClearWorldMap` |
| Voice    | 3 | ? | `VoiceData`, `RelayedVoiceData` |

All streams use the same frame format. QUIC priority: Default and Chunks
urgency 0, WorldMap urgency 1 (all incremental).

## Compression

Some packets are marked compressed (e.g. [[SetChunk]], [[SetColumn]],
`UpdateWorldMap`, `OpenWindow`). For these, the whole body is one zstd frame;
`payload_length` is the compressed size. An empty body is not compressed.

## Data types

All multi-byte numbers are little-endian, except `UUID`.

| Type                | Size     | Notes                                                       |
|---------------------|----------|-------------------------------------------------------------|
| `i8` / `u8`         | 1        |                                                             |
| `bool`              | 1        | 0 or 1                                                      |
| `i16`               | 2        |                                                             |
| `i32` / `u32`       | 4        |                                                             |
| `f32`               | 4        | IEEE float                                                  |
| `f64`               | 8        | IEEE double                                                 |
| `UUID`              | 16       | Two big-endian 64-bit integers (most significant first)     |
| `VarInt`            | 1-5      | Unsigned LEB128, see below                                  |
| `VarString`         | variable | `VarInt` byte length, then that many UTF-8 bytes            |
| fixed ASCII[n]      | n        | Null-padded ASCII                                           |
| `Position`          | 24       | 3 × `f64` (x, y, z)                                         |
| `Vector3d`          | 24       | 3 × `f64`                                                   |
| `Direction`         | 12       | 3 × `f32` (yaw, pitch, roll)                                |
| `HalfFloatPosition` | 6        | 3 × `i16`, fixed point: value / 10000 blocks                |
| vector3f            | 12       | 3 × `f32`                                                   |

## VarInt and VarString

`VarInt`: 7 value bits per byte, low bits first; high bit set means another
byte follows. At most 5 bytes.

```pseudo
function read_varint(bytes, offset):
    value = 0
    for i in 0 .. 4:
        byte = bytes[offset + i]            // error if truncated
        value |= (byte & 0x7F) << (7 * i)
        if (byte & 0x80) == 0:
            return (value, i + 1)           // value, bytes consumed
    error "VarInt longer than 5 bytes"

function write_varint(value):               // 0 <= value <= 0xFFFFFFFF
    out = []
    loop:
        byte = value & 0x7F
        value >>= 7
        if value == 0: return out + [byte]
        out.append(byte | 0x80)
```

`VarString` length counts bytes, not characters. Byte arrays use the same
`VarInt` length prefix.

## Nullable fields

Structures with optional or variable-length fields are laid out as:

1. Null bits: one or more `u8` bitfields; a set bit means the field is present.
2. Fixed block: fixed-size fields in order. An absent optional fixed field is
   still written, zero-filled.
3. Offset table, only if there are two or more variable-length fields: one
   `i32` per field, relative to the start of the variable block; `-1` when
   absent. A single variable-length field has no offset; it starts the
   variable block.
4. Variable block: `VarString`s, byte arrays and nested structures.

"Variable block starts at byte N" in packet descriptions is the size of
items 1-3.
