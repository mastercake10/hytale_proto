# World and Chunk Data

## Chunk grid

World columns are grouped in 32×32 chunks. A chunk coordinate is:

```text
cx = floor(x / 32)
cz = floor(z / 32)
local_x = floor(x) - cx * 32
local_z = floor(z) - cz * 32
```

## SetColumn (138)

`SetColumn` is a compact source of the top opaque block height for each column.
It is useful for ground-height estimates.

Layout of the payload after zstd decompression:

```packet
bound: client
summary: Compressed 32×32 height column
columns: Offset | Field Name | Field Type | Notes
0    | `x`       | `i32`
4    | `z`       | `i32`
8    | `height`  | `i32`[1024]      | 32 × 32, row-major by local z then local x. `-2147483648` is a sentinel for void/unknown
4104 | `tintmap` | `VarInt` + bytes | Length-prefixed tint data
```

The fixed block is 4104 bytes: 8 bytes of coordinates plus 4096 bytes of
heights. The variable block starts immediately after it.

## SetChunk (131)

`SetChunk` carries compressed block-section data. It is much larger than
`SetColumn`; only decode it when actual block contents are needed.

Layout after decompression:

```packet
bound: client
summary: Compressed chunk section data
columns: Offset | Field Name | Field Type | Notes
0  | Null bits      | `u8`         | bit0 local light, bit1 global light, bit2 data
1  | `x`            | `i32`        | Section coordinate, not block coordinate
5  | `y`            | `i32`        | Section coordinate, not block coordinate
9  | `z`            | `i32`        | Section coordinate, not block coordinate
13 | `local_light`  | `i32` offset | Relative to byte 25
17 | `global_light` | `i32` offset | Relative to byte 25
21 | `data`         | `i32` offset | Relative to byte 25
25 | Variable block | bytes        | Each field is a `VarInt` length followed by bytes
```

`x`, `y` and `z` are section coordinates. The first block in the section is at
`(x * 32, y * 32, z * 32)`.

### Block section data

The `data` field starts with the block palette, followed by the filler palette
and the rotation palette. Each palette begins with a `u8` palette type:

```text
0 Empty     no palette entries and no block array (all air)
1 HalfByte  up to 16 entries; packed nibbles
2 Byte      up to 256 entries; one byte per block
3 Short     up to 65536 entries; one u16 per block
```

For `HalfByte` and `Byte`, the palette is:

```text
u16 count
count x:
  u8  internal_id
  i32 external_id
  u16 block_count
```

followed by the block array:

- `HalfByte`: 16384 bytes. Each byte holds two nibbles; the high nibble is
  the even local index and the low nibble is the odd local index.
- `Byte`: 32768 bytes, one internal id per block.

For `Short`:

```text
u16 count
count x:
  u16 internal_id
  i32 external_id
  u16 block_count
```

followed by 32768 little-endian `u16` internal ids.

The local block index inside a 32×32×32 section is:

```text
index = ((y & 31) << 10) | ((z & 31) << 5) | (x & 31)
```

The filler and rotation palettes use the same type byte and palette layout;
their values are stored in their own palette arrays.

## ServerSetBlock (140)

One block update. This is the most direct confirmation that a block changed.

Layout (fixed size: 19 bytes):

```packet
bound: client
summary: One block update
columns: Offset | Field Name | Field Type | Notes
0  | `x`        | `i32`
4  | `y`        | `i32`
8  | `z`        | `i32`
12 | `block_id` | `i32` | `0` means air/empty
16 | `filler`   | `i16`
18 | `rotation` | `u8`  | See [Rotations](08-glossary.md#rotations)
```

## ServerSetBlocks (141)

A batch of block updates relative to an origin.

```packet
bound: client
summary: Batched block updates
columns: Offset | Field Name | Field Type | Notes
0  | `x`    | `i32`         | Section coordinate
4  | `y`    | `i32`         | Section coordinate
8  | `z`    | `i32`         | Section coordinate
12 | `cmds` | SetBlockCmd[] | `VarInt` count followed by commands
```

Each `SetBlockCmd` is 9 bytes:

| Offset | Field Name | Field Type | Notes |
|-------:|------------|------------|-------|
|      0 | `index`    | `i16`      | Local index inside the 32×32×32 section |
|      2 | `block_id` | `i32`      |       |
|      6 | `filler`   | `i16`      |       |
|      8 | `rotation` | `u8`       |       |

The world position of a command is `origin * 32 + local coordinate`, using the
same local index formula as `SetChunk`.

## UpdateBlockDamage (144)

Visual damage/progress update, not necessarily a final block change.

```packet
bound: client
summary: Block damage/progress display
```

## Chunk loading behavior

- The server may resend chunks after a new session or a major world update.
- Height data can arrive before or after the corresponding block sections.
- Caching height columns by chunk coordinate avoids repeated decompression.

## Block type ids

Block ids in chunk sections and block updates index the block-type list the
server sends at join in `UpdateBlockTypes` (zstd-compressed, same map header as
the other asset packets: `u8 nullBits`, `u8 UpdateType`, `i32 maxId`, `VarInt`
count, then `{i32 id, BlockType}` entries with no length prefix).

The ids are assigned when the server loads its assets: two servers running the
same game version use different numbering (the same id was `Rock_Stone` on one
and a plant block on another). Resolve names from the current join's list, never
from a table saved on another server.

`BlockType` layout used for names: 4 null-bit bytes, a 177-byte fixed block,
then 25 `i32` variable-field offsets, variable block at `+277`. The offset at
`+177` is the `item` string, at `+181` the block `name`. When present, `item` is
the first variable field (offset `0`), so `name` sits right after it. State
variants have their own id and a name like `*<Item>_State_Definitions_<State>`
while sharing the base `item`. Breaking behaviour lives in the item asset's
`BlockType.Gathering.Breaking.GatherType` (`Rocks`, `Woods`, `Soils`, ...), and
a tool's effect on it in its `Tool.Specs[].Power` for that gather type.
