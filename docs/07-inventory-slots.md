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

### InventorySection

```text
0  null bits                u8   bit0 items
1  capacity                 i16
3  variable block
   items: VarInt count, then count x (slot i32, ItemWithAllMetadata)
```

`ItemWithAllMetadata` is the same item structure used by inventory updates.
