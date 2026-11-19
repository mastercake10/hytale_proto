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

## Breaking blocks

`BreakBlockInteraction` is a `SimpleBlockInteraction` whose config decides what a
swing may break:

- `SoftOnly` refuses everything that is not a soft block, whatever is held.
- `Tool` + `MatchTool` name the tool the block wants; a held item that does not
  match fails the damage step.
- The world config can forbid breaking a block type outright
  (`WorldConfig.isBlockBreakingAllowed`).

With nothing in hand the interaction is still allowed to run
(`heldItemStack == null`), but it falls back to the plain block-damage path, so
only blocks that accept a bare hand (soft blocks) actually give way. Stone and
ore need a matching tool.

Root interaction ids belong to the **item**, not to the interaction type: the
server resolves the Primary root from the item *it* has in hand
(`InteractionContext.getRootInteractionId`) and runs the operations of that root.
The follow-on operations each carry their own root id too, and the whole set
differs per item.

Where the ids come from: set at asset load and delivered to the client as part
of the asset stream (see [[Interaction root assets]] below), so a client knows
them before its first swing. They are **stable for a given server build** and
**change when the server's asset table changes** — comparing captures from two
different server builds is what makes them look per-session. Same build, three
pickaxe classes:

| Held item | Op roots the server ran, in chain order |
|-----------|------------------------------------------|
| crude / copper / adamantite pickaxe | `2714`, `1273`, `1274`, `1275`, `5641` |
| hatchet | `2763`, `1164`, `1165`, `1166`, `4361` |
| bare hand | `3376`, `595`, `596`, `2573` (an older build: `3687`, `430`, `431`, `77`) |
| held block (Soil_Dirt) | `3296` |

A capture from an older build carried `3031`, `1108`, `1109`, `1110`, `5669` for
a pickaxe. The ids are dense indices into the server's root table, so a server
update reassigns them: `3031` now names `Boar_Ram`, `1108` a mace interaction.
An old capture therefore does not fail loudly — it points at unrelated roots,
which is why one skeleton cannot keep its own ids across a server update.

So a captured skeleton can be reused for another item of the same class, but
every op root has to be rewritten to the ids the server resolves for the item
actually held. The mapping is positional: template op `i` plays the server's op
`i`, so template `[3031, 1108, 1109, 1110, 5669]` becomes
`[2714, 1273, 1274, 1275, 5641]` for a crude pickaxe.

Consequences for replay (all observed on the wire):

- If the **first** op root is wrong, the server does not start the chain and does
  not cancel it either; it answers only when the queued chain times out (a few
  seconds), or its echo reveals the root it resolved. Learn the held item's
  Primary root from that echo, and the remaining op roots from the updates the
  server echoes as it advances through the chain.
- If a **later** op root is stale, the chain runs up to that op and then hangs
  until the timeout. Each replay learns one more op, so a second swing with the
  learned ids completes.
- The skeleton shape itself does differ by item **kind**, not by class: a tool
  swing and a bare-hand (or non-tool item) swing are different chains. Replaying
  the hand shape while a tool is held is cancelled immediately, and vice versa.
  Keep one capture per kind and swap the op roots.
- A `SetActiveSlot` correction or an immediate [[CancelInteractionChain]] (291)
  on the first update means the claimed hand (hotbar slot + item) is wrong; a
  cancel that arrives seconds later is the queue timeout, not the hand claim.

### Interaction root assets

Two asset packets carry the ids, both sent once at join:

- `UpdateRootInteractions` (**67**, zstd-compressed payload) — `Map<int, RootInteraction>`
  for the whole server: `mapMaxId` and every root asset. Observed on one build:
  6476 roots, 143 736 compressed bytes / 924 146 raw bytes.
  `RootInteraction` fixed block is 6 bytes with seven `i32` variable offsets at
  `6` (asset id string), `10` (`interactions: int[]`), `14` (cooldown),
  `18` (settings), `22` (rules), `26` (tags), `30` (hud input binding), variable
  block starting at `+34`; null bits are `id` (0), `cooldown` (1), `settings` (2),
  `tags` (3), `hudInputBindingEntry` (4). `InteractionRules` occupies a 17-byte
  fixed block but its variable block starts at `+33` (16 bytes of padding).
- `UpdateItems` (**54**) — every `ItemBase.interactions` is a
  `Map<InteractionType, int>`; this is the item's Primary/secondary root id.

The op roots a chain then runs are *not* the `interactions` array of that root.
For a pickaxe, root `2714` (`Pickaxe_Attack`) has a single entry, while the ops
that actually run are separate root assets named after the nested interactions
(`1273` = `**Pickaxe_Mine_Next_Interactions_0`, `1274` = `..._1`,
`1275` = `..._2`, `5641` = `*Tool_Pickaxe_Crude_InteractionVars_Pickaxe_Mine_Effect`).
The ids in `RootInteraction.interactions` do not index the root table — reading
`Pickaxe_Attack (2714) -> [274]` resolves `274` to an unrelated sword asset, and
the same holds for every root sampled — so the op set cannot be read off the root
graph alone: it also needs the `Interaction` asset table, a separate packet.

Practical rule: a captured skeleton is reusable across items of the same kind
once the op roots are rewritten positionally, and the mapping is worth caching
per `(item, build)`; detect a build change by hashing the asset table and drop
the cache when the hash moves. One throwaway swing per item per build recovers
the ids if the cache is empty: the echo of the first update names the root the
server resolved.

A swing that damages blocks also opens **forks**: `BlockDamage` runs the damage
step per selected block as a forked chain (`new_forks` on the update, later
updates carrying `forked_id` = entry/sub-entry indices). Each fork needs its own
`state 0` (Finished) update; an unreleased fork stops at progress `0.184` and the
whole chain never completes. Some ops are *hold* ops that run indefinitely until
the client sends `state 0` for them.

Ending a chain correctly means mirroring the server's own last echoed update with
`state 0` and `initial` false, and doing the same for every open fork. Sending a
template-shaped close instead misses a hold op or a fork, and a chain left open
makes every later chain queue behind it and time out.

One hit is the **whole chain**, not just its first packet: the initial update
starts the swing and the following updates carry the charge ramp (`progress`
rising). A capture of a real hold shows the exact cadence:

- one update per client tick, **~16.7 ms** apart (`~12 ms` in some captures), all
  with the same `chain_id`, for **~270 ms** - that is one held swing
- the chain is closed with a final update whose state is `0` (Finished)
- the next swing starts a **new chain id** about **84 ms** later

Matching that cadence is what makes a replay damage a block. Off-cadence
replays are accepted with no error and do nothing, and a chain that is never
closed stays open on the server: every later chain then queues behind it and
times out, so nothing breaks at all until the player reconnects. The server
validates the claimed hand (active hotbar slot + item, utility and tools slots)
against its own state, and every update after the first must arrive while the
chain is live, otherwise it is cancelled.

A held tool also carries a `BreakShape` (from `ItemTool`), so one swing damages
every block the shape selects around the target — a pickaxe breaks several
blocks at once, not one. In Creative the server skips the damage step entirely
and removes the selected blocks with no drops.

## Placing a block

Placing is a `Secondary` interaction on a **block item** in hand, and it takes
two packets (observed with `Rock_Stone_Cobble`):

1. The initial chain: `interaction_type = Secondary` (1), `initial = true`,
   `item_in_hand_id` set, `active_hotbar_slot`/`equip_slot` set.
   - `data.block_position` = the **clicked support block**, not the cell being
     filled.
   - Its `interaction_data` entries carry the item's secondary root (observed
     `3295`) and `block_face` on the entry that matches the clicked support
     (for example `1` = Up when placing on top of it).
2. Follow-up chain, same `chain_id`, `initial = false`, whose
   `interaction_data` names the placement root (observed `70`):
   - `block_position` = the **cell that receives the block** (support block
     offset by the face direction).
   - `block_face` = the same face.
   - `placed_block_id` = the block type id being placed (`943` for the cobble
     above).
   - `block_rotation` is present (all zeroes for an unrotated block).

So the position in the chain data and the position in the sync data are
different cells: the clicked block versus the filled cell.

The server side (`PlaceBlockInteraction`) reads the filled cell, face, rotation
and placed block id from the interaction **sync data** of that follow-up update,
and the support block from the chain data, then validates reach and places.

One placement is **three** client packets, all with the same `chain_id` and sent
about 16 ms apart (observed for a single right-click):

| # | `initial` | content |
|--:|-----------|---------|
| 1 | true      | secondary interaction, item in hand, support block in the chain data |
| 2 | false     | placement root, sync `state = 4` (NotFinished) |
| 3 | false     | placement root, sync `state = 0` (Finished) |

After that the client keeps sending low-cost updates for the item's root (state 4)
for as long as the button is held. `interaction_data` entries whose
`block_position` is absent belong to the item's other operations; only the entry
for the placement root carries the filled cell.

After those three the client sends one more update whose only entry is the
item's own root with `state = 0` (Finished). That update matters: without it the
chain stays pending, and while it is pending the server's interruption rules
(`applyRules` → `validateBlocked`) refuse **every** later `Secondary` interaction
for that player, including their own placements, until they reconnect. The same
silence applies — nothing is cancelled, the new chains are simply not run.

Note: a client packet that is dropped before the chain is created produces no
`CancelInteractionChain` (291) at all — silence is not acceptance.

## Attacking an entity

A melee attack on an entity is the **same chain as a block swing** with one
difference: the chain data carries the target's network id instead of a block
position.

- `data.entity_id` = the target's network id, `data.block_position` absent.
- **The target the server acts on is the `hit_entities` list in the interaction
  sync data**, not the chain data: `ClientSourcedSelector` reads
  `clientState.hitEntities` and resolves each entry by `networkId`
  (`SelectedHitEntity`: network id, hit location, position, body rotation). A
  chain that only carries `data.entity_id` is accepted and does nothing.
  Observed: the client only puts `hit_entities` on some operations of the chain
  (the `operation_base_index = 5` updates in the capture), so a replay has to
  rewrite both the chain data and those entries.
- Same interaction type (`Primary`), same cadence: one update every ~16.7 ms for
  about 200 ms, then a final update with `state = 0`.
- The chain carries the same hand validation (active hotbar slot, item, utility
  and tools slots) as any other interaction.

Entity positions come from `EntityUpdates` (161), which is a stream of records:

| part | layout |
|------|--------|
| header | `nullBits` u8, `networkId` i32, two i32 offsets (removed, updates) relative to `header + 13` |
| removed | `VarInt count`, then `count` x i32 network ids |
| updates | `VarInt count`, then components |

Each component is `VarInt typeId` followed by its body, and **no length prefix** —
so the stream can only be walked with a size table. The useful ones are fixed
size: `Transform` (9) is 49 bytes (`nullBits`, position 3 x f64, rotation 3 x
f32), `MovementStates` (10) 4, `Block` (6) 8, `Prediction` (20) 16, `Mounted` (22)
47; several flags are zero-length. `NewSpawn` (23) is empty — the record's
network id is the entity.

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
