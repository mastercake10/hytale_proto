# Interaction Chains

## SyncInteractionChains (290)

This packet is bidirectional and contains up to 128 chain updates.

```packet
bound: both
summary: Interaction chain state updates
`update_count` | `VarInt`                     | Up to 128
`update`       | chain update[`update_count`] | See [Chain update](#chain-update)
```

## Chain update

Each update has a fixed 60-byte header followed by a variable block.

Header layout:

| Offset | Field Name                  | Field Type | Notes                                        |
|-------:|-----------------------------|------------|----------------------------------------------|
|      0 | Null bits                   | `u8`       | Bits 0–6 select optional fields; bit7 unused |
|      1 | `active_hotbar_slot`        | `i32`      |                                              |
|      5 | `active_utility_slot`       | `i32`      |                                              |
|      9 | `active_tools_slot`         | `i32`      |                                              |
|     13 | Flags                       | `u8`       | bit0 `initial`, bit1 `desync`                |
|     14 | `override_root_interaction` | `i32`      |                                              |
|     18 | `interaction_type`          | `u8`       | See [Interaction types](#interaction-types)  |
|     19 | `equip_slot`                | `i32`      |                                              |
|     23 | `chain_id`                  | `i32`      | See [Chain IDs](#chain-ids)                  |
|     27 | `state`                     | `u8`       | See [States](#states)                        |
|     28 | `operation_base_index`      | `i32`      |                                              |
|     32 | `item_in_hand_offset`       | `i32`      | Variable-block offset; `-1` when absent      |
|     36 | `utility_item_offset`       | `i32`      | Variable-block offset; `-1` when absent      |
|     40 | `tools_item_offset`         | `i32`      | Variable-block offset; `-1` when absent      |
|     44 | `forked_id_offset`          | `i32`      | Variable-block offset; `-1` when absent      |
|     48 | `data_offset`               | `i32`      | Variable-block offset; `-1` when absent      |
|     52 | `new_forks_offset`          | `i32`      | Variable-block offset; `-1` when absent      |
|     56 | `interaction_data_offset`   | `i32`      | Variable-block offset; `-1` when absent      |

Null bits at byte 0 map to the seven optional fields in the same order as the
offset slots:

| Bit | Field              |
|----:|--------------------|
|   0 | `item_in_hand_id`  |
|   1 | `utility_item_id`  |
|   2 | `tools_item_id`    |
|   3 | `forked_id`        |
|   4 | `data`             |
|   5 | `new_forks`        |
|   6 | `interaction_data` |

The seven offset slots occupy bytes 32–59. Each offset is relative to the start
of the variable block (byte 60), not to the start of the packet. A value of `-1`
means that field is absent. The fixed header therefore consists of 32 bytes of
fields plus 28 bytes of offset slots.

## Variable fields

| Field                                                 | Encoding                                                                                                                              |
|-------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `item_in_hand_id`, `utility_item_id`, `tools_item_id` | `VarString`                                                                                                                           |
| `forked_id`                                           | [ForkedChainId](#forkedchainid)                                                                                                       |
| `data`                                                | [InteractionChainData](#interactionchaindata)                                                                                         |
| `new_forks`                                           | `VarInt` count followed by that many chain updates                                                                                    |
| `interaction_data`                                    | `VarInt` count, a presence bitfield of `ceil(count / 8)` bytes, then one [InteractionSyncData](#interactionsyncdata) for each set bit |

The `interaction_data` entries are serialized in set-bit order and are matched
to operations using `operation_base_index`.

## ForkedChainId

Fixed block: 9 bytes, followed by an optional nested `ForkedChainId`.

| Offset | Field Name    | Field Type    | Notes                         |
|-------:|---------------|---------------|-------------------------------|
|      0 | Null bits     | `u8`          | bit0 nested forked id present |
|      1 | `entry_index` | `i32`         |                               |
|      5 | `sub_index`   | `i32`         |                               |
|      9 | `forked_id`   | ForkedChainId | Optional nested value         |

The nested value starts immediately at byte 9; there is no offset slot.

## InteractionChainData

Fixed block: 61 bytes, followed by an optional `hit_detail` string.

| Offset | Field Name       | Field Type  | Notes                                                                    |
|-------:|------------------|-------------|--------------------------------------------------------------------------|
|      0 | Null bits        | `u8`        | bit0 hit location, bit1 block position, bit2 hit normal, bit3 hit detail |
|      1 | `entity_id`      | `i32`       |                                                                          |
|      5 | `proxy_id`       | `UUID`      | 16 bytes                                                                 |
|     21 | `hit_location`   | vector3f    | Optional; 3 × `f32`                                                      |
|     33 | `block_position` | 3 × `i32`   | Optional                                                                 |
|     45 | `target_slot`    | `i32`       |                                                                          |
|     49 | `hit_normal`     | vector3f    | Optional; 3 × `f32`                                                      |
|     61 | `hit_detail`     | `VarString` | Optional; no offset slot, always last                                    |

## InteractionSyncData

Fixed data occupies bytes 0–156. Two offset slots occupy bytes 157–164, so the
variable block starts at byte 165. Offsets are relative to byte 165; `-1` means
absent.

| Offset | Field Name                 | Field Type | Notes                                                         |
|-------:|----------------------------|------------|---------------------------------------------------------------|
|      0 | Null bits                  | `u8`       | see below                                                     |
|      1 | Null bits 2                | `u8`       | bit0 `hit_entities`                                           |
|      2 | `state`                    | `u8`       | See [States](#states)                                         |
|      3 | `progress`                 | `f32`      |                                                               |
|      7 | `operation_counter`        | `i32`      |                                                               |
|     11 | `root_interaction`         | `i32`      |                                                               |
|     15 | `total_forks`              | `i32`      |                                                               |
|     19 | `entity_id`                | `i32`      |                                                               |
|     23 | `entered_root_interaction` | `i32`      |                                                               |
|     27 | `block_position`           | 3 × `i32`  | Optional                                                      |
|     39 | `block_face`               | `u8`       | See [Block faces](08-glossary.md#block-faces)                 |
|     40 | `block_rotation`           | 3 × `u8`   | Optional; see [Rotations](08-glossary.md#rotations)           |
|     43 | `placed_block_id`          | `i32`      |                                                               |
|     47 | `charge_value`             | `f32`      |                                                               |
|     51 | `chaining_index`           | `i32`      |                                                               |
|     55 | `flag_index`               | `i32`      |                                                               |
|     59 | `attacker_pos`             | 3 × `f64`  | Optional                                                      |
|     83 | `attacker_rot`             | 3 × `f32`  | Optional                                                      |
|     95 | `raycast_hit`              | 3 × `f64`  | Optional                                                      |
|    119 | `raycast_distance`         | `f32`      |                                                               |
|    123 | `raycast_normal`           | 3 × `f32`  | Optional                                                      |
|    135 | `movement_direction`       | `u8`       | See [Movement directions](08-glossary.md#movement-directions) |
|    136 | `apply_force_state`        | `u8`       | See [Apply-force states](08-glossary.md#apply-force-states)   |
|    137 | `next_label`               | `i32`      |                                                               |
|    141 | `generated_uuid`           | `UUID`     | Optional; 16 bytes                                            |
|    157 | `fork_counts_offset`       | `i32`      | Relative to byte 165                                          |
|    161 | `hit_entities_offset`      | `i32`      | Relative to byte 165                                          |

Null bits at byte 0:

| Bit | Field            |
|----:|------------------|
|   0 | `block_position` |
|   1 | `block_rotation` |
|   2 | `attacker_pos`   |
|   3 | `attacker_rot`   |
|   4 | `raycast_hit`    |
|   5 | `raycast_normal` |
|   6 | `generated_uuid` |
|   7 | `fork_counts`    |

`fork_counts` is a `VarInt` count followed by `(u8 interaction_type, i32 count)`
pairs. `hit_entities` is a `VarInt` count followed by that many
`SelectedHitEntity` values.

### SelectedHitEntity

| Offset | Field Name      | Field Type | Notes                                                |
|-------:|-----------------|------------|------------------------------------------------------|
|      0 | Null bits       | `u8`       | bit0 hit location, bit1 position, bit2 body rotation |
|      1 | `network_id`    | `i32`      |                                                      |
|      5 | `hit_location`  | vector3f   | Optional; 3 × `f32`                                  |
|     17 | `position`      | 3 × `f64`  | Optional                                             |
|     41 | `body_rotation` | 3 × `f32`  | Optional                                             |

Fixed size: 53 bytes.

## Chain IDs

Observed rules:

- Client-started chains use positive ids.
- Server-started chains use negative ids.
- For a new client chain, the server requires `chain_id > lastClientChainId`.
- Later updates reuse the same chain id.
- The counter is monotonic for the lifetime of the player entity/session.
- A new session or entity recreation resets the counter.

## Start validation

Before a client chain starts, the server checks at least:

- `initial` is true for a start packet.
- `forked_id` is null for a new root chain.
- chain data is present.
- the chain id is positive and above the last client chain id.
- active hotbar/utility/tool slots match the live inventory.
- the item ids in the packet match the live inventory.
- the root interaction exists and is allowed by world config.
- interruption/blocking rules allow the chain to start.

A slot mismatch cancels the chain and sends a
[[SetActiveSlot]] correction.

## Use distance validation

Block interactions that reach a block (`SimpleBlockInteraction`, which includes
container opening) are validated server-side by
`InteractionValidation.canEntityInteractWithBlock`:

- The distance is measured from the **server's player transform plus eye
  height** to the block centre.
- The allowed radius is the held item's interaction config `useDistance` for
  the current game mode, plus a 2-block buffer.
- In Creative the radius is also compared against
  `PlayerCreativeSettings.creativeInteractionDistance`, which the client sends
  in `SyncPlayerPreferences` (116) at offset `+8` as an `i32`; the server
  clamps it to `0..128`.
- `attacker_pos`, `attacker_rot`, `raycast_hit` and `raycast_normal` in
  `InteractionSyncData` are optional context fields and are not used for this
  range check.

## Root interaction resolution

Start validation resolves a *root interaction id* from the chain's
`interaction_type` and the held item (`InteractionContext.getRootInteractionId`),
then looks it up in the loaded assets. Ids travel in `InteractionSyncData` as
`root_interaction` (offset `11`) and `entered_root_interaction` (offset `23`).

The lookup has two different failure paths, which look different on the wire:

- **Blocked or missing for this type** (`getRootInteractionId` returns null, or
  the root is disabled by world config): the chain is rejected *immediately*
  with [[CancelInteractionChain]] (291). The same happens for a chain id at or
  below `lastClientChainId`, a forked chain started by the client, missing
  chain data, or a negative/zero chain id.
- **Id not found in the asset set** (`RootInteraction.getRootInteractionOrUnknown`
  returns null): the server does not start and does not reject. The start packet
  stays queued and the client receives 291 only after the operation timeout,
  roughly 3 s later. An id captured from an older game build reaches this path.

A chain that is never answered is therefore usually a stale root interaction id,
not a distance or slot problem: those two produce an immediate cancel and a
[[SetActiveSlot]] correction respectively.

## Queueing

Chains are consumed from a per-player queue. If another chain with blocking
rules is active, a new chain can be queued. A chain that waits too long in the
queue is canceled with [[CancelInteractionChain]]
(291).

## Teleporter blocks

A teleporter block carries a `Teleporter` component (a warp) and a
`TeleporterInteraction` block interaction (`SimpleBlockInteraction`). Travel is
therefore an ordinary block interaction — the client sends a chain aiming at the
block, and the server does the rest:

- `interactWithBlock` fails when the block entity has no `Teleporter`, when the
  player is still waiting for the client to be ready, or when the entity already
  carries `Teleport`, `PendingTeleport` or `UsedTeleporter`.
- On success it adds `Teleport` (destination from `teleporter.toTeleport(...)`)
  and `UsedTeleporter(worldUuid, position, clearoutXZ = 1.3, clearoutY = 2.5)`.
  Those defaults mean the player must move at least 1.3 blocks in XZ or 2.5 in Y
  away from the arrival point before any teleporter can be used again.
- The move reaches the client as `ClientTeleport` (109), the same packet as any
  other server-side teleport.

Links are one-way: the destination is the block's own warp, so using A lands at
B without B gaining a route back to A. A teleporter whose state is not `default`
is reset to its default variant when used.

## States

| Value | Name        |
|------:|-------------|
|     0 | Finished    |
|     1 | Skip        |
|     2 | ItemChanged |
|     3 | Failed      |
|     4 | NotFinished |

## Interaction types

Common values:

| Value | Name          |
|------:|---------------|
|     0 | Primary       |
|     1 | Secondary     |
|     2 | Ability1      |
|     3 | Ability2      |
|     4 | Ability3      |
|     5 | Ability4      |
|     6 | Use           |
|     7 | Pick          |
|     8 | Pickup        |
|    11 | Collision     |
|    13 | SwapTo        |
|    14 | SwapFrom      |
|    25 | GameModeSwap  |
|    26 | OnBreak       |
|    27 | OnBreakImpact |

## CancelInteractionChain (291)

```packet
bound: client
summary: Chain cancellation
columns: Offset | Field Name | Field Type | Notes
0 | Null bits  | `u8`                   | bit0: forked id present
1 | `chain_id` | `i32`
5 | Forked id  | optional ForkedChainId | Entry/sub-entry indices only; it does not contain a separate chain id
```

A cancellation can refer to a queued or active chain. The optional
`ForkedChainId` starts immediately at byte 5 and has no offset slot.
