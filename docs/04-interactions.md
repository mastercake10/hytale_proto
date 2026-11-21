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

At chain start the server resolves the root from the chain's `interaction_type`
and the item **it** sees in the player's hand (`getRootInteractionId`); the
client's `root_interaction` values are checked against that, not trusted. Two
failure paths look different on the wire:

- **No root for this type, or blocked by world config** — immediate
  [[CancelInteractionChain]] (291). Same for a bad chain id, a client-started
  fork or missing chain data.
- **Root id unknown in the server's asset set** — no start and no cancel; the
  queued chain is cancelled only after the timeout (~3 s).

A chain that is never answered therefore usually carries a wrong root id; a
wrong hand claim gives an immediate cancel plus a [[SetActiveSlot]] correction.

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

## Interaction assets

The client receives everything it needs to run interactions once, at join, as
zstd-compressed asset packets. Both start with `u8 nullBits` (bit0 = map
present), `u8 UpdateType`, `i32 maxId`, then at offset `6` a `VarInt` count and
`count` entries `{i32 id, value}`; entries come in hash order, not by id.

**`UpdateRootInteractions` (67)** — value is a `RootInteraction`:

| Offset | Field | Type |
|---:|---|---|
| 0 | null bits | `u8` — bit0 id, bit1 cooldown, bit2 settings, bit3 tags, bit4 hud binding |
| 1 | `clickQueuingTimeout` | `f32` |
| 5 | `requireNewClick` | `bool` |
| 6..30 | offsets of id, `interactions`, cooldown, settings, rules, tags, hud binding | 7 × `i32` |
| 34 | variable block | |

`id` is the asset name; `interactions` (`VarInt n` + n × `i32`) are ids into
packet 66. `InteractionRules` has a 17-byte fixed block but its variable block
starts at `+33`.

**`UpdateInteractions` (66)** — value is `VarInt typeId` + an `Interaction` body.
Bodies have **no length prefix**; the end is only found by walking every
variable field. Common prefix:

| Offset | Field | Type |
|---:|---|---|
| 0 | null bits | `u8` — bit0 effects, bit1 settings, bit2 tags, bit3 camera, higher bits per type |
| 1 | `waitForDataFrom` | `u8` — 0 Client, 1 Server, 2 None |
| 2 | `horizontalSpeedMultiplier` | `f32` |
| 6 | `runTime` | `f32` (seconds) |
| 10 | `onItemChangeBehavior` | `i32` |
| 14 | type fields, then `i32` variable offsets | `-1` = absent |

Variable offsets follow the order effects, settings, rules (always present),
tags, camera, then type-specific fields. Most types share the `Simple` layout
with `next` at `+14` and `failed` at `+18` (interaction ids). `Condition` and
`Wielding` have two null-bit bytes, which shifts their fields by one
(`Condition`: `runTime` `+7`, `next` `+15`, `failed` `+19`, then optional
game-mode / movement requirements). Child references:

| Type (typeId) | Children | Refer to |
|---|---|---|
| `Simple`-like | `next`, `failed` | interaction ids |
| `Serial` (29) | list | interaction ids |
| `Chaining` (11) | list (+ optional flag map) | interaction ids |
| `Parallel` (23) | list | **root** ids |
| `Replace` (15) | `defaultValue` (`+14`), variable name (string) | **root** id |
| `Select` (20) | `hitEntity` (`+23`) | **root** id |

Other typeIds used by tools: 0 SimpleBlock, 1 Simple, 2 PlaceBlock,
3 BreakBlock, 5 UseBlock, 12 Condition, 17 ChangeState, 21 DamageEntity.

**Items to roots.** `ItemBase.interactions` in `UpdateItems` (54) maps an
interaction type to the item's root. By name, the same link is: a referenced
root (e.g. `Hatchet_Attack`); an inline definition becomes the root
`*<Item>_Interactions_<Type>`; item variables used by `Replace` become
`*<Item>_InteractionVars_<Var>` (inherited from the item's `Parent`). Block items
without their own entry use `Block_Primary`; an empty hand uses
`*Empty_Interactions_Primary`. Interactions nested inline in another asset get
roots named after their path (e.g. `**<Asset>_Next_Interactions_<i>`).

**Id stability.** Ids are assigned when the server loads its assets. They were
stable across reconnects, but after a server restart the same asset set came
back numbered differently. Always use the tables from the current join, never
ids stored from an earlier session.

## Running a chain

A root compiles into a flat list of operations (`OperationsBuilder`; the client
does the same). `operation_counter` is an index into that list.

- An interaction with `next` or `failed` emits itself, then its `next` inline,
  then a `Jump` to the end if `failed` is set, then its `failed` branch inline.
  Failing jumps to the start of the failed branch (or past `next` when there is
  none). A `Jump` takes an index of its own.
- `Serial` emits only its children, inline.
- `Chaining` emits itself, then `child; Jump(end)` for each child, and continues
  at the child selected by `chaining_index`.
- Every other type is one operation. `Parallel` and `Replace` targets are roots
  that run separately.

Each **executed** operation produces exactly one `InteractionSyncData` entry, in
execution order, with `operation_counter` and the `root_interaction` that owns
the operation. Entry indices count across entered roots:

- **Enter a root** (`Replace`, `Parallel` child 0, a successful `UseBlock`):
  the next entry is counter 0 of the new root; when it runs out, the caller
  resumes at the calling operation + 1.
- **Fork** (`Parallel` children 1..n): a separate chain with the same
  `chain_id`, `forked_id = (entry index of the Parallel, k - 1)`, starting at
  entry 0. A fork of a fork nests its id.
- An update carries entries `operation_base_index ..` up to the newest one; the
  server drops buffered entries past the end of each update, so always re-send
  through the latest entry.

What each operation reports (state values in [[#States]]):

| Operation | Client result |
|---|---|
| `Simple`, `Select` | NotFinished until `runTime` has elapsed, then Finished |
| `Chaining` | Finished, `chaining_index` = chosen child |
| `Jump`, `Parallel`, `Replace` | Finished at once (`Replace` with no target: Failed) |
| `UseBlock` | Failed when the block has no use action → its failed branch |
| `ChangeState` | Failed when the block has no matching state |
| `Condition` | Finished if every requirement it sets (game mode, jumping, crouching, …) matches the player, else Failed |
| `BreakBlock` | Finished, with `block_position` and `block_face` |

The chain's own `state` is 4 while any operation runs and 0 when the last one
finished; every fork must reach 0 as well.

**What the server checks.** For each entry: `operation_counter` and
`root_interaction` must equal the server's own run (otherwise desync and the
rest of the client data is dropped), entries must be contiguous, fork ids and
chain ids must be right, a finished entry may not go back to NotFinished, and
`chaining_index` must be in range. `BreakBlock` uses the entry's
`block_position` (reach-checked); `Select` takes its end from the client and its
targets from `hit_entities`. The server keeps its **own clock**: `progress` is
not read, `runTime` is enforced server-side, and the progress it sends back is
its own.

**Timeouts.** The threshold is about `2 × ping + 3 s`. A chain is cancelled when
an operation waits for client data longer than that, or when client and server
disagree about the chain being finished for longer than that. A chain that the
client never finishes stays active and blocks later chains of the same kind
(rules / `validateBlocked`) until it times out or the player reconnects.

## Breaking blocks

Breaking is the held item's **Primary** chain aimed at a block
(`interaction_type` 0, `data.block_position` = target). Its operations come
entirely from the item's root (see above), so the entry sequence differs per
tool class: the block-break step sits at a different place, and in a different
fork, for a pickaxe, a hatchet, a shovel or a bare hand. Swapping ids inside
another item's sequence leaves the break step without its `BreakBlock` entry —
the chain completes normally but deals no damage.

`BreakBlockInteraction` decides what may break:

- `SoftOnly` refuses everything but soft blocks.
- `Tool` / `MatchTool` require a matching tool for the damage step.
- `WorldConfig.isBlockBreakingAllowed` can forbid a block type.
- With nothing in hand only blocks that accept a bare hand give way.
- A tool's `BreakShape` damages every block the shape selects around the target.
- In Creative the damage step is skipped and selected blocks are removed.

Damage per swing comes from the tool's spec for the block's gather type, so a
block takes several swings. The client starts the next swing (a new chain id)
shortly after the previous chain finished.

## Placing a block

Placing is the held block item's **Secondary** chain (`interaction_type` 1),
run like any other chain (see [[#Running a chain]]):

- `data.block_position` = the **clicked support block**; entries name the
  clicked side in `block_face` (e.g. `1` = Up).
- The entry of the `PlaceBlock` operation carries the **cell that receives the
  block** (support offset by the face) in `block_position`, plus `block_face`,
  `block_rotation` and `placed_block_id`. `PlaceBlockInteraction` reads those
  from the sync data and the support block from the chain data, then checks
  reach.
- The chain must be finished like any other (`state 0` on the item's root). A
  placement chain left open blocks every later `Secondary` interaction of that
  player through the interruption rules, silently — no cancel is sent.

## Opening a container

Opening a chest is the held item's **Use** chain (`interaction_type` 6) aimed at
the block (`data.block_position`). Its entries name the item's Use root (an item
without its own uses `*Empty_Interactions_Use`) and, for the step that acts on
the block, the block's own Use root (`Open_Container` for chests). Like every
root id these are renumbered at server start, so a recorded open chain only works
again once its root ids are translated to the current tables. A chain with stale
ids gets no window back (see [[#Root interaction resolution]]).

Observed (one server build, chest `Furniture_Crude_Chest_Large`): the open chain
has the **same shape for every held item**, including block stacks, tools, a
broken tool (durability 0) and an empty slot. It is one initial packet, state 0,
with four entries: `(op 0, item Use root)`, `(op 1, item Use root, block_position,
block_face)`, `(op 0, Open_Container, block_position, block_face)`,
`(op 2, item Use root)`. The server answers with `OpenWindow` (200), then echoes
the chain with state 0. Closing the window sends `CloseWindow` (202).

The server queues an initial chain it cannot start yet
(`InteractionManager.syncStart` returns false when interaction rules or a
cooldown block it). It cancels the chain only after
`2 x average tick ping + 3000 ms` (`PacketHandler.getOperationTimeoutThreshold`).
While that chain sits at the head of the queue, later initial chains from the
same player are not started. Observed: an open sent while the player was about
200 blocks above the chest (out of reach) was echoed with only its first entry
and state 4 (NotFinished), then cancelled about 6 s later. Opens sent from
within reach of the chest worked.

Open_Container keeps one window per player per container
(`windows.putIfAbsent(uuid, ...)`). An open while that player's window on the
same block is still registered does nothing.

## Attacking an entity

A melee attack is the item's **Primary** chain with the target in the chain
data (`data.entity_id` = network id, no block position). The server acts on
the `hit_entities` list of the `Select` entries (`SelectedHitEntity`: network
id, hit location, position, body rotation, read by `ClientSourcedSelector`),
not on `data.entity_id`; a chain without `hit_entities` completes and does
nothing. Hand validation is the same as for every chain.

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
