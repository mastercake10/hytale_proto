# Inventory and Active Slots

## Inventory sections

| Section id | Section   |
|-----------:|-----------|
| -1  | Hotbar    |
| -2  | Storage   |
| -3  | Armor     |
| -5  | Utility   |
| -8  | Tools     |
| -9  | Backpack  |
| -11 | Abilities |
| -12 | Rune bag  |

## UpdatePlayerInventory (170)

Player inventory contents. zstd-compressed. Variable block at byte 33; each
offset is relative to it, `-1` when absent. Every field is an
[InventorySection](#inventorysection).

```packet
bound: client
summary: Inventory contents
columns: Offset | Field Name | Field Type | Notes
0  | Null bits       | `u8`         | bit0..bit7 = fields below in order
1  | `storage`       | `i32` offset |
5  | `armor`         | `i32` offset |
9  | `hotbar`        | `i32` offset |
13 | `utility`       | `i32` offset |
17 | `tools`         | `i32` offset |
21 | `backpack`      | `i32` offset |
25 | `ability_slots` | `i32` offset |
29 | `rune_bag`      | `i32` offset |
33 | Variable block  | bytes        |
```

## SetActiveSlot (177)

Fixed 8 bytes, uncompressed.

```packet
bound: both
summary: Active slot of an inventory section
columns: Offset | Field Name | Field Type | Notes
0 | `inventory_section_id` | `i32` | See [Inventory sections](#inventory-sections)
4 | `active_slot`          | `i32` | `-1` = none
```

Server to client: sets the active slot of a section, e.g. a hotbar correction
(`-1`) after a rejected chain.

Client to server (non-hotbar sections, e.g. utility, tools), checked in this order; each failure
disconnects:

| Condition | Disconnect reason |
|-----------|-------------------|
| section `-1` (hotbar) | `hotbarChangeWithoutInteraction` |
| unknown section | `invalidInventorySection` |
| `active_slot < -1` or `>= capacity` | `hotbarSlotOutOfRange` |
| slot already active | `hotbarSlotAlreadySelected` |

If server logic cancels or alters the change, the server answers with
`SetActiveSlot` carrying the resulting slot.

## Selecting a hotbar slot

Hotbar selection is an interaction, not a `SetActiveSlot`. The client sends
[[SyncInteractionChains]] with `interaction_type` `SwapFrom` (14) (a `SwapTo`
(13) chain also occurs):

| Field | Value |
|-------|-------|
| `active_hotbar_slot` | slot being left |
| `data.target_slot` ([InteractionChainData](04-interactions.md#interactionchaindata) offset 45) | new slot, `0..8` |

The server runs `ChangeActiveSlotInteraction` (root `*Default_Swap`), sets the
hotbar slot and forks `SwapTo`. On all non-swap chains `active_hotbar_slot` is
the current slot. Chain updates sent right after a swap may still carry the
previous `active_hotbar_slot`.

## Validation coupling

[Chain starts](04-interactions.md#chain-update) carry `active_hotbar_slot`,
`active_utility_slot`, `active_tools_slot` and optional `item_in_hand_id`,
`utility_item_id`, `tools_item_id`. All must match the server's inventory; a
mismatch cancels the chain, and the server may send a corrective
`SetActiveSlot`.

## Container windows

Container contents (chests, benches, backpacks) are never in chunk or block
data; they arrive only in window packets.

| Step | Packet |
|------|--------|
| Open (block interaction, see [Opening a container](04-interactions.md#opening-a-container)) | [[OpenWindow]] with full contents |
| Container changes | [[UpdateWindow]] with the full [InventorySection](#inventorysection), sent on the next inventory tick |
| Client moves items | `SendWindowAction` (203) |
| Close | [[CloseWindow]], either direction |

The server closes a block window ([[CloseWindow]]) when, on a position update or
teleport, the player is more than 7.0 blocks from the block, or the block no
longer has the same item type.

`WindowType`: 0 Container, 1 PocketCrafting, 2 BasicCrafting, 3 DiagramCrafting,
4 StructuralCrafting, 5 Processing, 6 Memories, 7 AbilityBench.

### OpenWindow (200)

zstd-compressed. Variable block at byte 18.

```packet
bound: client
summary: Open a container window and send its contents
columns: Offset | Field Name | Field Type | Notes
0  | Null bits         | `u8`  | bit0 `window_data`, bit1 `inventory`, bit2 `extra_resources`
1  | `id`              | `i32` | Window id for update/close
5  | `window_type`     | `u8`  | `WindowType`
6  | `window_data`     | `i32` offset | VarString JSON; container blocks: `{"blockItemId": "<item id>"}`
10 | `inventory`       | `i32` offset | [InventorySection](#inventorysection)
14 | `extra_resources` | `i32` offset | `ExtraResources`
18 | Variable block    | bytes | Offsets relative to byte 18, `-1` absent
```

Chest block items: `Furniture_<Style>_Chest_Small` / `Furniture_<Style>_Chest_Large`
(e.g. `Furniture_Crude_Chest_Small`, `Furniture_Dungeon_Chest_Epic_Large`).
Slot count is `InventorySection.capacity`.

### UpdateWindow (201)

zstd-compressed. Variable block at byte 17. Replaces the window contents.

```packet
bound: client
summary: Replace an open window's contents
columns: Offset | Field Name | Field Type | Notes
0  | Null bits         | `u8`  | bit0 `window_data`, bit1 `inventory`, bit2 `extra_resources`
1  | `id`              | `i32` | Window id from `OpenWindow`
5  | `window_data`     | `i32` offset | As in `OpenWindow`
9  | `inventory`       | `i32` offset | [InventorySection](#inventorysection)
13 | `extra_resources` | `i32` offset |
17 | Variable block    | bytes | Offsets relative to byte 17, `-1` absent
```

### CloseWindow (202)

Fixed 4 bytes, uncompressed.

```packet
bound: both
summary: Close an open container window
columns: Offset | Field Name | Field Type | Notes
0 | `id` | `i32` | Window id from `OpenWindow`
```

### InventorySection

```text
0  null bits   u8    bit0 items
1  capacity    i16
3  items       VarInt count, then count × (i32 slot, ItemWithAllMetadata)
```

### ItemWithAllMetadata

Variable block at byte 34; offsets relative to it.

```text
0  null bits             u8    bit0 metadata
1  quantity              i32
5  durability            f64   current; 0 with max 0 = no durability
13 max_durability        f64
21 quality               i32
25 override_drop_anim    bool
26 item_id offset        i32   VarString
30 metadata offset       i32   VarString; valid when bit0 set
34 variable block
```
