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
1  | `x`            | `i32`
5  | `y`            | `i32`
9  | `z`            | `i32`
13 | `local_light`  | `i32` offset | Relative to byte 25
17 | `global_light` | `i32` offset | Relative to byte 25
21 | `data`         | `i32` offset | Relative to byte 25
25 | Variable block | bytes        | Each field is a `VarInt` length followed by bytes
```

The section `data` layout is not documented yet.

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
0  | `x`    | `i32`         | Origin
4  | `y`    | `i32`         | Origin
8  | `z`    | `i32`         | Origin
12 | `cmds` | SetBlockCmd[] | `VarInt` count followed by commands
```

Each `SetBlockCmd` is 9 bytes:

| Offset | Field Name | Field Type | Notes |
|-------:|------------|------------|-------|
|      0 | `index`    | `i16`      |       |
|      2 | `block_id` | `i32`      |       |
|      6 | `filler`   | `i16`      |       |
|      8 | `rotation` | `u8`       |       |

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
