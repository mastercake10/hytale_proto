# Packet Framing and Streams

The transport is QUIC. Application packets are framed inside QUIC streams.

## Frame format

Every application packet uses this envelope.

Layout:

| Field Name       | Field Type             | Notes                                                  |
|------------------|------------------------|--------------------------------------------------------|
| `payload_length` | `u32`                  | Counts only the packet body, not the eight-byte header |
| `packet_id`      | `u32`                  | See [Packet IDs](packets.md)                           |
| `payload`        | `payload_length` bytes | Packet body, described per packet                      |

Both header fields are little-endian.

A reader has to buffer stream data until a complete header and body are
available. Because every frame carries its length, a packet with an unknown ID
can be skipped without parsing its body.

## Streams

- The main bidirectional stream carries the normal client/server packet flow.
- The server also opens auxiliary streams for bulk world data such as chunks,
  columns and map updates.
- Auxiliary streams use the same frame envelope.

## Compression

Several world-data packets contain zstd-compressed sections. Compression is
per-packet body content, not a QUIC-level feature.
[[SetChunk]] (131) and
[[SetColumn]] (138) are the two most common
examples.

## Data types

| Type                | Size     | Notes                                                          |
|---------------------|----------|----------------------------------------------------------------|
| `i8`                | 1        | Signed 8-bit integer                                           |
| `u8`                | 1        | Unsigned 8-bit integer                                         |
| `bool`              | 1        |                                                                |
| `f16`               | 2        | IEEE half float                                                |
| `i16`               | 2        | Signed 16-bit integer                                          |
| `i32`               | 4        | Signed 32-bit integer                                          |
| `u32`               | 4        | Unsigned 32-bit integer                                        |
| `f32`               | 4        | IEEE float                                                     |
| `f64`               | 8        | IEEE double                                                    |
| `UUID`              | 16       | Two big-endian 64-bit integers                                 |
| `VarInt`            | variable | Compact variable-length integer encoding                       |
| `VarString`         | variable | `VarInt` byte length followed by exactly that many UTF-8 bytes |
| fixed ASCII[n]      | n        | Null-padded ASCII                                              |
| `Position`          | 24       | 3 × `f64`                                                      |
| `Vector3d`          | 24       | 3 × `f64`                                                      |
| `Direction`         | 12       | 3 × `f32`                                                      |
| `HalfFloatPosition` | 6        | 3 × `f16`                                                      |
| vector3f            | 12       | 3 × `f32`                                                      |

## VarInt and VarString

`VarInt` is an unsigned LEB128 value. The reader accepts at most five bytes,
which covers the 32-bit range used by the protocol. Each byte contributes seven
value bits; the high bit means another byte follows.

```pseudo
function read_varint(bytes, offset):
    value = 0
    shift = 0

    for i in 0 .. 4:
        if offset + i >= len(bytes):
            error "truncated VarInt"

        byte = bytes[offset + i]
        value = value | ((byte & 0x7F) << shift)

        if (byte & 0x80) == 0:
            return (value, i + 1)    // value and bytes consumed

        shift = shift + 7

    error "VarInt is longer than five bytes"

function write_varint(value):
    if value < 0 or value > 0xFFFFFFFF:
        error "VarInt out of range"

    out = []
    loop:
        byte = value & 0x7F
        value = value >> 7

        if value != 0:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return out
```

`VarString` is a `VarInt` byte length followed by UTF-8 bytes. The length counts
bytes, not characters.

```pseudo
function read_varstring(bytes, offset):
    (length, prefix_size) = read_varint(bytes, offset)
    start = offset + prefix_size
    end = start + length

    if end > len(bytes):
        error "truncated VarString"

    return (decode_utf8(bytes[start:end]), prefix_size + length)

function write_varstring(text):
    data = encode_utf8(text)
    return write_varint(len(data)) + data
```

When reading a packet body, keep the returned byte counts so the next field
starts at the correct offset.

## Nullable fields

Nullable fields are usually controlled by a bitfield at the start of the
structure ("null bits"), with offsets into a variable block later in the packet.
