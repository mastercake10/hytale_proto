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
