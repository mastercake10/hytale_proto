# Inventory and Active Slots

## UpdatePlayerInventory (170)

Server-to-client inventory snapshot/update. It establishes the hotbar and
utility item contents that interaction-chain validation uses. Layout not
documented yet.

```packet
bound: client
summary: Inventory contents
```

## SetActiveSlot (177)

Layout (fixed size: 8 bytes, both directions):

```packet
bound: both
summary: Active hotbar slot correction/update
columns: Offset | Field Name | Field Type | Notes
0 | `inventory_section_id` | `i32` | `-1` in a correction from the server
4 | `active_slot`          | `i32` | The actual active slot
```

Observed server behavior:

- A correction from the server uses `inventory_section_id = -1` with the actual
  active slot.
- Sending a client-to-server active-slot change with section `-1` outside an
  interaction is rejected as `hotbarChangeWithoutInteraction`.
- Active slot changes that are part of a normal interaction are represented by
  interaction chains, not by a standalone slot packet.

## Selecting a hotbar slot

Changing the active hotbar slot (the client's number-key / scroll selection) is
an interaction, not a `SetActiveSlot`. The server defines a
`ChangeActiveSlotInteraction` (root `*Default_Swap`) whose `TargetSlot` is
validated to the range `0..8`; running it calls `setActiveSlot` on the hotbar
component and forks a `SwapTo` interaction.

A client can therefore trigger a slot change itself by sending that
interaction (`SyncInteractionChains` (290) with `interaction_type` `SwapTo`
(13) or `SwapFrom` (14) and `data.target_slot` set to the wanted slot); no
`SetActiveSlot` packet is involved, so it is not rejected as
`hotbarChangeWithoutInteraction`. Observed client behaviour: after the server
takes such a swap the client's own chain updates keep reporting the previous
`active_hotbar_slot` for a short while, so a reader must not treat the first
report after a swap as authoritative.

Observed on the wire, a key press emits an interaction-chain update with:

- `interaction_type` = `SwapFrom` (14) — a `SwapTo` (13) chain also occurs.
- `active_hotbar_slot` = the slot being **left** (the previous selection).
- `data.target_slot` (the `InteractionChainData` field at offset 45) = the
  **new** slot.

So the newly selected slot is `data.target_slot` on a swap chain, not
`active_hotbar_slot`. On every non-swap interaction `active_hotbar_slot` already
is the current slot. Example sequence for pressing `1` then `8` while the
selection moves 7 -> 0 -> 7:

```
it=SwapFrom active_hotbar_slot=7 target_slot=0
it=SwapFrom active_hotbar_slot=0 target_slot=7
```

## Validation coupling

[Interaction-chain](04-interactions.md#chain-update) start packets embed:

- `active_hotbar_slot`
- `active_utility_slot`
- `active_tools_slot`
- optional `item_in_hand_id`, `utility_item_id`, `tools_item_id`

All of these must agree with the server's live inventory. A mismatch cancels the
chain and may send a corrective `SetActiveSlot`.

## Container windows

Container contents (chests, benches, backpacks) are **not** part of chunk or
block data. They are sent only through window packets:

- `OpenWindow` (200) when the container window is opened.
- `UpdateWindow` (201) whenever the open window's container is marked dirty.

Both packets are zstd-compressed (`IS_COMPRESSED = true`).

Server flow for a chest:

1. A block interaction (`OpenContainerInteraction`) resolves the block's
   `ItemContainerBlock`.
2. It creates a `ContainerBlockWindow` (window type `Container = 0`) and calls
   `PageManager.setPageWithWindows(...)`.
3. `WindowManager.openWindow` builds `OpenWindow` with the window id, window
   data, and `inventory = itemContainer.toPacket()` — this is the first time the
   contents reach the client.
4. A container change event marks the window dirty. The inventory send system
   tick calls `WindowManager.updateWindows()`, which writes an `UpdateWindow`
   with a fresh `InventorySection`.
5. Closing sends `CloseWindow` (202); client moves arrive as `SendWindowAction`
   (203) / window actions.

### OpenWindow (200)

```packet
bound: client
summary: Open a container window and send its contents
columns: Offset | Field Name | Field Type | Notes
0  | Null bits       | `u8`  | bit0 `windowData`, bit1 `inventory`, bit2 `extraResources`
1  | `id`            | `i32` | Window id used by later update/close packets
5  | `window_type`   | `u8`  | `WindowType`; `0` = Container
6  | `window_data` offset | `i32` | Relative to variable block at byte 18; `-1` absent
10 | `inventory` offset   | `i32` | Relative to byte 18; `-1` absent
14 | `extraResources` offset | `i32` | Relative to byte 18; `-1` absent
18 | Variable block  | bytes |
```

`window_data` is a JSON string (`blockItemId` for container blocks).

### UpdateWindow (201)

```packet
bound: client
summary: Replace an open window's contents
columns: Offset | Field Name | Field Type | Notes
0  | Null bits       | `u8`  | bit0 `windowData`, bit1 `inventory`, bit2 `extraResources`
1  | `id`            | `i32` | Window id from `OpenWindow`
5  | `window_data` offset | `i32` | Relative to variable block at byte 17; `-1` absent
9  | `inventory` offset   | `i32` | Relative to byte 17; `-1` absent
13 | `extraResources` offset | `i32` | Relative to byte 17; `-1` absent
17 | Variable block  | bytes |
```

### CloseWindow (202)

Client to server. The body is not compressed.

```packet
bound: server
summary: Close an open container window
columns: Offset | Field Name | Field Type | Notes
0 | `id` | `i32` | Window id from `OpenWindow`
```

### InventorySection

```text
0  null bits                u8   bit0 items
1  capacity                 i16
3  variable block
   items: VarInt count, then count x (slot i32, ItemWithAllMetadata)
```

`ItemWithAllMetadata` is the same item structure used by inventory updates.

### ItemWithAllMetadata

Observed layout, checked against three captured container windows (142, 1272
and 1797 items). Offsets are from the start of the item; the variable block
starts at byte 34.

```text
0  null bits            u8   bit0 metadata present
1  quantity             i32
5  durability           f64  current; 0 with max 0 = item has no durability
13 max durability       f64
21 quality              i32
25 override drop anim   bool
26 item id offset       i32  relative to byte 34; item id is a VarString
30 metadata offset      i32  relative to byte 34; valid when null bit 0 is set
34 variable block
```

### Chest item ids

The container comes from the block at the interaction position, so the item
id in `window_data` identifies the chest type.

| Item id                              | Shape |
|--------------------------------------|-------|
| `Furniture_Crude_Chest_Small`        | small |
| `Furniture_Goblin_Chest_Small`       | small |
| `Furniture_Crude_Chest_Large`        | large |
| `Furniture_Dungeon_Chest_Epic_Large` | large |
| `Furniture_Temple_Wind_Chest_Large`  | large |
| `Furniture_Feran_Chest_Large`        | large |
| `Furniture_Temple_Light_Chest_Large` | large |
Observed client/server behaviour:

- Moving or teleporting away while the window is open produces `CloseWindow`
  (202) from the server; the container window is validated on position changes.
