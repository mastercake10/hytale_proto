# World and Chunk Data

## Chunk grid

Columns are grouped in 32×32 chunks; block sections are 32×32×32.

```text
cx = floor(x / 32)              local_x = floor(x) - cx * 32
cz = floor(z / 32)              local_z = floor(z) - cz * 32
index = ((y & 31) << 10) | ((z & 31) << 5) | (x & 31)   // local index in a section
```

[[SetColumn]] and [[SetChunk]] for the same chunk arrive in no fixed order.

## SetColumn (138)

Top opaque block height per column. zstd-compressed. Fixed block 4104 bytes;
variable block starts right after it.

```packet
bound: client
summary: Compressed 32×32 height column
columns: Offset | Field Name | Field Type | Notes
0    | `x`       | `i32`            | Chunk coordinate
4    | `z`       | `i32`            | Chunk coordinate
8    | `height`  | `i32`[1024]      | Row-major by local z, then local x. `-2147483648` = void/unknown
4104 | `tintmap` | `VarInt` + bytes | Length-prefixed tint data
```

## SetChunk (131)

One block section. zstd-compressed.

```packet
bound: client
summary: Compressed chunk section data
columns: Offset | Field Name | Field Type | Notes
0  | Null bits      | `u8`         | bit0 `local_light`, bit1 `global_light`, bit2 `data`
1  | `x`            | `i32`        | Section coordinate
5  | `y`            | `i32`        | Section coordinate
9  | `z`            | `i32`        | Section coordinate
13 | `local_light`  | `i32` offset | Relative to byte 25, `-1` absent
17 | `global_light` | `i32` offset | Relative to byte 25, `-1` absent
21 | `data`         | `i32` offset | Relative to byte 25, `-1` absent
25 | Variable block | bytes        | Each field: `VarInt` length + bytes
```

The section's first block is at `(x * 32, y * 32, z * 32)`.

### Block section data

`data` holds three palettes in order: block, filler, rotation. All three use
the same format: a `u8` palette type, then entries, then the per-block array.

| Type | Name     | Entries   | Entry layout                                   | Block array |
|-----:|----------|-----------|------------------------------------------------|-------------|
| 0    | Empty    | none      | -                                              | none (all air / 0) |
| 1    | HalfByte | ≤ 16      | `u16 count`, then `u8 internal_id, i32 external_id, u16 block_count` | 16384 bytes, two nibbles per byte: high = even index, low = odd index |
| 2    | Byte     | ≤ 256     | as HalfByte                                    | 32768 × `u8` |
| 3    | Short    | ≤ 65536   | `u16 count`, then `u16 internal_id, i32 external_id, u16 block_count` | 32768 × `u16` LE |

The array holds internal ids indexed by the local index; the palette maps them
to external ids (block type id, filler, rotation).

## ServerSetBlock (140)

One block update. Fixed size 19 bytes.

```packet
bound: client
summary: One block update
columns: Offset | Field Name | Field Type | Notes
0  | `x`        | `i32`
4  | `y`        | `i32`
8  | `z`        | `i32`
12 | `block_id` | `i32` | `0` = air/empty
16 | `filler`   | `i16`
18 | `rotation` | `u8`  | See [Rotations](08-glossary.md#rotations)
```

## ServerSetBlocks (141)

Batched block updates in one section.

```packet
bound: client
summary: Batched block updates
columns: Offset | Field Name | Field Type | Notes
0  | `x`    | `i32`         | Section coordinate
4  | `y`    | `i32`         | Section coordinate
8  | `z`    | `i32`         | Section coordinate
12 | `cmds` | SetBlockCmd[] | `VarInt` count + commands
```

`SetBlockCmd`, 9 bytes. World position = `section * 32 + local`, local from
`index` via the [Chunk grid](#chunk-grid) formula.

| Offset | Field Name | Field Type |
|-------:|------------|------------|
|      0 | `index`    | `i16`      |
|      2 | `block_id` | `i32`      |
|      6 | `filler`   | `i16`      |
|      8 | `rotation` | `u8`       |

## UpdateBlockDamage (144)

Block damage display; not a block change. Fixed size 21 bytes, uncompressed.

```packet
bound: client
summary: Block damage/progress display
columns: Offset | Field Name | Field Type | Notes
0  | Null bits  | `u8`  | bit0 `position`
1  | `position` | `i32` × 3 | x, y, z; zero-filled when absent
13 | `damage`   | `f32` |
17 | `delta`    | `f32` |
```

## Block type ids

Block ids in sections and block updates index the block-type list sent at join
in `UpdateBlockTypes` (zstd-compressed; asset map header `u8 nullBits`,
`u8 UpdateType`, `i32 maxId`, `VarInt` count, then `{i32 id, BlockType}`
entries without length prefix).

Ids are assigned when the server loads its assets, in no fixed order. They are
stable while the server runs and change between server starts. Always resolve
names from the current join's list.

`BlockType` name fields: 177-byte fixed block (first 4 bytes are null bits),
then 25 `i32` variable-field offsets, variable block at `+277`.

| Offset | Field  | Notes |
|-------:|--------|-------|
| `+177` | `item` | VarString; when present it is the first variable field (offset `0`) |
| `+181` | `name` | VarString |

State variants have their own id, a name like
`*<Item>_State_Definitions_<State>`, and share the base `item`.

Breaking: the item asset's `BlockType.Gathering.Breaking.GatherType`
(`Rocks`, `Woods`, `Soils`, ...) selects which `Tool.Specs[].Power` of a tool
applies.
