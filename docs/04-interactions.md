# Interaction Chains

## SyncInteractionChains (290)

```packet
bound: both
summary: Interaction chain state updates
`update_count` | `VarInt`                     | Max 128
`update`       | chain update[`update_count`] | See [Chain update](#chain-update)
```

## Chain update

Fixed header of 60 bytes, then the variable block. The seven offset slots
(bytes 32–59) are relative to byte 60; `-1` = absent.

| Offset | Field Name                  | Field Type | Notes                                       |
|-------:|-----------------------------|------------|---------------------------------------------|
|      0 | Null bits                   | `u8`       | bits 0–6 = the seven optional fields below  |
|      1 | `active_hotbar_slot`        | `i32`      |                                             |
|      5 | `active_utility_slot`       | `i32`      |                                             |
|      9 | `active_tools_slot`         | `i32`      |                                             |
|     13 | Flags                       | `u8`       | bit0 `initial`, bit1 `desync`               |
|     14 | `override_root_interaction` | `i32`      |                                             |
|     18 | `interaction_type`          | `u8`       | See [Interaction types](#interaction-types) |
|     19 | `equip_slot`                | `i32`      |                                             |
|     23 | `chain_id`                  | `i32`      | See [Chain IDs](#chain-ids)                 |
|     27 | `state`                     | `u8`       | See [States](#states)                       |
|     28 | `operation_base_index`      | `i32`      |                                             |
|     32 | `item_in_hand_id` offset    | `i32`      | null bit 0                                  |
|     36 | `utility_item_id` offset    | `i32`      | null bit 1                                  |
|     40 | `tools_item_id` offset      | `i32`      | null bit 2                                  |
|     44 | `forked_id` offset          | `i32`      | null bit 3                                  |
|     48 | `data` offset               | `i32`      | null bit 4                                  |
|     52 | `new_forks` offset          | `i32`      | null bit 5                                  |
|     56 | `interaction_data` offset   | `i32`      | null bit 6                                  |

## Variable fields

| Field                                                 | Encoding                                                                                                                  |
|-------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| `item_in_hand_id`, `utility_item_id`, `tools_item_id` | `VarString`                                                                                                               |
| `forked_id`                                           | [ForkedChainId](#forkedchainid)                                                                                           |
| `data`                                                | [InteractionChainData](#interactionchaindata)                                                                             |
| `new_forks`                                           | `VarInt` count + that many chain updates                                                                                  |
| `interaction_data`                                    | `VarInt` count, presence bitfield of `ceil(count / 8)` bytes, then one [InteractionSyncData](#interactionsyncdata) per set bit |

`interaction_data` entries are in set-bit order; entry `i` is operation entry
`operation_base_index + i`.

## ForkedChainId

| Offset | Field Name    | Field Type    | Notes                                   |
|-------:|---------------|---------------|-----------------------------------------|
|      0 | Null bits     | `u8`          | bit0 nested `forked_id` present         |
|      1 | `entry_index` | `i32`         |                                         |
|      5 | `sub_index`   | `i32`         |                                         |
|      9 | `forked_id`   | ForkedChainId | Optional; inline, no offset slot        |

## InteractionChainData

| Offset | Field Name       | Field Type  | Notes                                                                    |
|-------:|------------------|-------------|--------------------------------------------------------------------------|
|      0 | Null bits        | `u8`        | bit0 hit location, bit1 block position, bit2 hit normal, bit3 hit detail |
|      1 | `entity_id`      | `i32`       |                                                                          |
|      5 | `proxy_id`       | `UUID`      |                                                                          |
|     21 | `hit_location`   | 3 × `f32`   | Optional                                                                 |
|     33 | `block_position` | 3 × `i32`   | Optional                                                                 |
|     45 | `target_slot`    | `i32`       |                                                                          |
|     49 | `hit_normal`     | 3 × `f32`   | Optional                                                                 |
|     61 | `hit_detail`     | `VarString` | Optional; inline, no offset slot                                         |

## InteractionSyncData

Fixed data bytes 0–156, two offset slots at 157–164, variable block at 165
(offsets relative to 165, `-1` = absent).

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
|    141 | `generated_uuid`           | `UUID`     | Optional                                                      |
|    157 | `fork_counts` offset       | `i32`      |                                                               |
|    161 | `hit_entities` offset      | `i32`      |                                                               |

Null bits (byte 0): bit0 `block_position`, bit1 `block_rotation`,
bit2 `attacker_pos`, bit3 `attacker_rot`, bit4 `raycast_hit`,
bit5 `raycast_normal`, bit6 `generated_uuid`, bit7 `fork_counts`.

- `fork_counts`: `VarInt` count + `(u8 interaction_type, i32 count)` pairs.
- `hit_entities`: `VarInt` count + that many `SelectedHitEntity`.

### SelectedHitEntity

Fixed size 53 bytes.

| Offset | Field Name      | Field Type | Notes                                                |
|-------:|-----------------|------------|------------------------------------------------------|
|      0 | Null bits       | `u8`       | bit0 hit location, bit1 position, bit2 body rotation |
|      1 | `network_id`    | `i32`      |                                                      |
|      5 | `hit_location`  | 3 × `f32`  | Optional                                             |
|     17 | `position`      | 3 × `f64`  | Optional                                             |
|     41 | `body_rotation` | 3 × `f32`  | Optional                                             |

## States

| Value | Name        |
|------:|-------------|
|     0 | Finished    |
|     1 | Skip        |
|     2 | ItemChanged |
|     3 | Failed      |
|     4 | NotFinished |

## Interaction types

| Value | Name             | Value | Name            |
|------:|------------------|------:|-----------------|
|     0 | Primary          |    14 | SwapFrom        |
|     1 | Secondary        |    15 | Death           |
|     2 | Ability1         |    16 | Wielding        |
|     3 | Ability2         |    17 | ProjectileSpawn |
|     4 | Ability3         |    18 | ProjectileHit   |
|     5 | Ability4         |    19 | ProjectileMiss  |
|     6 | Use              |    20 | ProjectileBounce|
|     7 | Pick             |    21 | Held            |
|     8 | Pickup           |    22 | HeldOffhand     |
|     9 | CollisionEnter   |    23 | Equipped        |
|    10 | CollisionLeave   |    24 | Dodge           |
|    11 | Collision        |    25 | GameModeSwap    |
|    12 | EntityStatEffect |    26 | OnBreak         |
|    13 | SwapTo           |    27 | OnBreakImpact   |

## CancelInteractionChain (291)

```packet
bound: client
summary: Chain cancellation
columns: Offset | Field Name | Field Type | Notes
0 | Null bits  | `u8`                   | bit0: forked id present
1 | `chain_id` | `i32`
5 | Forked id  | optional ForkedChainId | Inline, no offset slot
```

Refers to a queued or active chain.

## Chain IDs

- Client-started chains: positive ids. Server-started: negative.
- A new client chain must have `chain_id > lastClientChainId`; later updates
  reuse the id.
- The counter is per player entity; it resets when the entity is recreated
  (e.g. on reconnect).

## Start validation

A client chain starts only if:

- `initial` is set, `forked_id` is null (clients cannot start forks), `data`
  is present;
- the chain id is valid (see [Chain IDs](#chain-ids));
- active hotbar/utility/tool slots and item ids match the server inventory;
- a root exists for `interaction_type` and the item the **server** sees in hand,
  and world config allows it;
- interruption/blocking rules and cooldowns allow it (else it is queued, see
  [Queueing and timeouts](#queueing-and-timeouts)).

Server responses on failure:

| Failure | Response |
|---|---|
| Slot / item mismatch | [[CancelInteractionChain]] + [[SetActiveSlot]] correction |
| Bad chain id, client fork, missing data, no root for type, blocked by world config | Immediate [[CancelInteractionChain]] |
| Root id unknown to the server's asset set | Nothing; cancelled at the timeout |

The client's `root_interaction` values are checked against the server-resolved
root, never trusted.

## Use distance validation

Applies to block interactions (`SimpleBlockInteraction`, incl. container open,
place, break):

- Distance: server-side player position + eye height → block centre.
- Limit: held item's `UseDistance` for the current game mode + 2 blocks.
  Default `UseDistance` (no `InteractionConfig` on the item): Adventure 5,
  Creative 6; game modes missing from an item's map use 1.
- Creative: also limited by `creativeInteractionDistance` from
  `SyncPlayerPreferences` (116), `i32` at offset `+8`, clamped to `0..128`.
- `attacker_pos`, `attacker_rot`, `raycast_hit`, `raycast_normal` are not used.

An out-of-reach chain is not started; it is answered with state 4 and cancelled
at the timeout.

Entity damage (`DamageEntityInteraction`) uses the same limit, measured from
the player's eye (position + eye height) to the target's **feet** position
(`canPlayerInteractWithEntity`). It is checked when the server runs the damage
entry, against the server-side player position at that moment.

## Item pickup

Dropped item entities are picked up by a player within the item's pickup
radius (item `ItemEntityConfig.PickupRadius`, else the world gameplay config;
default 1.75 blocks) after a pickup delay (default 0.5 s).

## Queueing and timeouts

- Chains are processed from a per-player queue. An initial chain that rules or a
  cooldown prevent from starting stays queued; while it is at the head, later
  initial chains of that player are not started.
- Cooldown: keyed by the root's id (or the cooldown's `Id`, shared between
  roots). Without a cooldown on the root or its game-mode settings, `Primary`,
  `Secondary`, `Use`, `Ability1-4`, `Pick`, `SwapFrom/To` etc. use **0.35 s**;
  collision, projectile, pickup, `OnBreak*`, `GameModeSwap`,
  `EntityStatEffect` use 0. Repeated swings of one root therefore start at
  most every 0.35 s, however fast the client sends them; the surplus waits in
  the queue.
- Default blocking: `Primary`, `Secondary`, `Use`, `Ability1-4`, `Pick` are
  blocked by any running chain of those types; `SwapFrom/To` by each other;
  `Held`, `HeldOffhand`, `Equipped`, `Dodge`, `GameModeSwap` by their own type.
- Timeout = `2 × average tick ping + 3000 ms`. Cancelled with
  [[CancelInteractionChain]] when:
  - a queued chain waits longer than that;
  - an operation waits for client data longer than that;
  - client and server disagree on the chain being finished for longer than that.
- A chain the client never finishes stays active and blocks later chains of the
  same kind until it times out or the player reconnects.

## Interaction assets

Sent once at join, zstd-compressed. Both packets: `u8` null bits (bit0 = map
present), `u8 UpdateType`, `i32 maxId`, then at offset 6 a `VarInt` count and
`count × {i32 id, value}` (hash order, not sorted).

**`UpdateRootInteractions` (67)** — value is a `RootInteraction`:

| Offset | Field | Type |
|---:|---|---|
| 0 | null bits | `u8` — bit0 id, bit1 cooldown, bit2 settings, bit3 tags, bit4 hud binding |
| 1 | `clickQueuingTimeout` | `f32` |
| 5 | `requireNewClick` | `bool` |
| 6..30 | offsets: id, `interactions`, cooldown, settings, rules, tags, hud binding | 7 × `i32` |
| 34 | variable block | |

`id` is the asset name; `interactions` = `VarInt n` + `n × i32` ids into
packet 66. `InteractionRules`: 17-byte fixed block, variable block at `+33`.

**`UpdateInteractions` (66)** — value is `VarInt typeId` + `Interaction` body,
**no length prefix** (end found only by walking every variable field). Common
prefix:

| Offset | Field | Type |
|---:|---|---|
| 0 | null bits | `u8` — bit0 effects, bit1 settings, bit2 tags, bit3 camera, higher bits per type |
| 1 | `waitForDataFrom` | `u8` — 0 Client, 1 Server, 2 None |
| 2 | `horizontalSpeedMultiplier` | `f32` |
| 6 | `runTime` | `f32` seconds |
| 10 | `onItemChangeBehavior` | `i32` |
| 14 | type fields, then `i32` variable offsets | `-1` = absent |

Variable offsets order: effects, settings, rules (always present), tags,
camera, then type-specific. `Simple`-layout types: `next` at `+14`, `failed`
at `+18`. `Condition` and `Wielding` have two null-bit bytes, shifting fields by
one (`Condition`: `runTime` `+7`, `next` `+15`, `failed` `+19`, then optional
game-mode / movement requirements).

| Type (typeId) | Children | Refer to |
|---|---|---|
| `Simple`-like | `next`, `failed` | interaction ids |
| `Serial` (29) | list | interaction ids |
| `Chaining` (11) | list (+ optional flag map) | interaction ids |
| `Parallel` (23) | list | **root** ids |
| `Replace` (15) | `defaultValue` (`+14`), variable name (string) | **root** id |
| `Select` (20) | `hitEntity` (`+23`) | **root** id |

Other typeIds: 0 SimpleBlock, 1 Simple, 2 PlaceBlock, 3 BreakBlock, 5 UseBlock,
12 Condition, 17 ChangeState, 21 DamageEntity.

**Items to roots.** `ItemBase.interactions` in `UpdateItems` (54) maps
interaction type → root id. Root naming:

| Source | Root name |
|---|---|
| Referenced root | its name, e.g. `Hatchet_Attack` |
| Inline item definition | `*<Item>_Interactions_<Type>` |
| Item variable used by `Replace` | `*<Item>_InteractionVars_<Var>` (inherited from `Parent`) |
| Block item without own entry | `Block_Primary` |
| Empty hand | `*Empty_Interactions_<Type>` |
| Inline in another asset | path-based, e.g. `**<Asset>_Next_Interactions_<i>` |

**Id stability.** Ids are assigned at server asset load: stable for the server's
lifetime, different after a restart. Use only the tables from the current join.

## Running a chain

A root compiles to a flat operation list (same on client and server);
`operation_counter` indexes it.

- Interaction with `next`/`failed`: itself, `next` inline, `Jump(end)` if
  `failed` is set, then `failed` inline. Failure jumps to the failed branch (or
  past `next` if none). `Jump` occupies an index.
- `Serial`: its children inline, nothing for itself.
- `Chaining`: itself, then `child; Jump(end)` per child; continues at the child
  selected by `chaining_index`.
- Any other type: one operation. `Parallel`/`Replace` targets are separate roots.

Each **executed** operation yields exactly one `InteractionSyncData` entry, in
execution order, carrying `operation_counter` and the owning `root_interaction`.
Entry indices run across entered roots:

- **Enter a root** (`Replace`, `Parallel` child 0, successful `UseBlock`): next
  entry is counter 0 of the new root; on its end, the caller resumes at calling
  operation + 1.
- **Fork** (`Parallel` children 1..n): separate chain, same `chain_id`,
  `forked_id = (entry index of the Parallel, k - 1)`, entries from 0. A fork of
  a fork nests its id.
- Each update carries entries `operation_base_index` through the newest; the
  server drops buffered entries past the end of an update, so always re-send
  through the latest entry.

Client result per operation:

| Operation | Result |
|---|---|
| `Simple`, `Select` | NotFinished until `runTime` elapsed, then Finished |
| `Chaining` | Finished, `chaining_index` = chosen child |
| `Jump`, `Parallel`, `Replace` | Finished immediately (`Replace` without target: Failed) |
| `UseBlock` | Failed if the block has no use action (→ failed branch) |
| `ChangeState` | Failed if the block has no matching state |
| `Condition` | Finished if all set requirements (game mode, jumping, crouching, …) match, else Failed |
| `BreakBlock` | Finished, with `block_position`, `block_face` |

Chain `state` is 4 while any operation runs, 0 when the last finished; every
fork must also reach 0.

**Server checks per entry:** `operation_counter` and `root_interaction` equal
the server's own run (else desync, remaining client data dropped); entries
contiguous; fork and chain ids correct; no Finished → NotFinished; 
`chaining_index` in range. The server runs its own clock: `progress` is ignored,
`runTime` enforced server-side, and the progress it sends is its own.

## Breaking blocks

Held item's **Primary** chain (`interaction_type` 0), `data.block_position` =
target. The operation sequence comes from the item's root, so the position (and
fork) of the `BreakBlock` entry differs per tool class. A chain whose sequence
lacks the `BreakBlock` entry completes but deals no damage. Each swing is a new
chain.

Breaking rules:

- `SoftOnly`: only soft blocks.
- `Tool` / `MatchTool`: damage requires a matching tool.
- `WorldConfig.isBlockBreakingAllowed` can forbid a block type.
- Empty hand: only blocks that accept a bare hand.
- Tool `BreakShape`: damages every block the shape selects around the target.
- Creative: no damage step; selected blocks are removed.
- Damage per swing: tool spec for the block's gather type.
- Server-side failures (the `BreakBlock` entry comes back Failed, no damage):
  target section unloaded, target block id 0 or 1, or the distance check
  (`InteractionValidation.canEntityInteractWithBlock`) fails.
- If the target cell has a non-zero **filler** value (part of a multi-cell
  block), the server retargets the chain to the base cell; the echoed
  `data.block_position` then differs from the one sent.

## Placing a block

Held block item's **Secondary** chain (`interaction_type` 1):

- `data.block_position` = clicked support block; `block_face` = clicked side
  (`1` = Up).
- The `PlaceBlock` entry carries the target cell (support + face offset) in
  `block_position`, plus `block_face`, `block_rotation`, `placed_block_id`.
  Reach is checked.
- The chain must finish (`state 0` on the item's root). An unfinished placement
  chain silently blocks all later `Secondary` interactions (no cancel sent).

## Opening a container

Held item's **Use** chain (`interaction_type` 6), `data.block_position` =
container. The sequence is the same for any held item (block, tool, broken
tool, empty hand). Chest, one initial packet, chain `state 0`, four entries:

| # | `operation_counter` | `root_interaction` | Extra |
|--:|--:|---|---|
| 0 | 0 | item Use root (`*Empty_Interactions_Use` if none) | |
| 1 | 1 | item Use root | `block_position`, `block_face` |
| 2 | 0 | block Use root (`Open_Container`) | `block_position`, `block_face` |
| 3 | 2 | item Use root | |

Server answers with `OpenWindow` (200), then echoes the chain with state 0.
Closing sends `CloseWindow` (202). One window per player per container: opening
while that player's window on the block is still registered does nothing.

## Attacking an entity

Item's **Primary** chain, `data.entity_id` = target network id, no block
position. Damage targets come only from `hit_entities` of the `Select` entries
([SelectedHitEntity](#selectedhitentity)); `data.entity_id` is not used. A chain
without `hit_entities` completes and does nothing.

Entity positions come from `EntityUpdates` (161):

| Part | Layout |
|------|--------|
| packet header | `u8` null bits (bit 0 removed, bit 1 updates), `i32` removed offset, `i32` updates offset; variable block at 9 |
| removed | `VarInt` count + `count × i32` network ids the client must drop |
| updates | `VarInt` count + `EntityUpdate` records |

`EntityUpdate`: `u8` null bits, `i32 networkId`, `i32` removed offset, `i32`
updates offset; variable block at 13. Its `removed` is `VarInt` count +
`count × u8` **component types** removed from that entity (not entity ids);
its `updates` is `VarInt` count + components.

Component = `VarInt typeId` + body, **no length prefix** (needs a size table).
Fixed sizes: `Block` (6) 8, `Transform` (9) 49 (`ModelTransform`: null bits
1 position / 2 body / 4 look; position 3 × `f64` @1, body orientation
yaw/pitch/roll 3 × `f32` @25, look orientation 3 × `f32` @37; absent parts
zero-filled), `MovementStates` (10) 4, `Prediction` (20) 16, `Mounted`
(22) 47; several flag components are 0 bytes. `NewSpawn` (23) is empty; the
record's network id is the new entity.

`ActiveAnimations` (24) is variable-sized: `VarInt` count, then
`ceil(count / 8)` presence bytes (bit *i* of byte *i/8* set = slot *i* present),
then one `VarString` per present slot, in slot order. Slots are
`AnimationSlot`: 0 Movement, 1 Status, 2 Action, 3 Face, 4 Emote,
5 ServerAction (the server always sends 6). Example: Status = `Alerted` only →
`06 02 07 41 6C 65 72 74 65 64`. The server queues this component only when the
entity becomes visible to a player (snapshot); later animation changes are sent
as [PlayAnimation (162)](09-other-packets.md#playanimation-162), not as
component updates.

An id in the packet-level `removed` array means the entity left the player's
view: out of view range, despawned, or dead. A dead NPC stays (corpse, death
animation) until its role's `DeathAnimationTime` has passed
(`DeferredCorpseRemoval`), then it is removed. An entity that comes back into
view reuses its network id.

## Teleporter blocks

A teleporter block has a `Teleporter` component (warp) and a
`TeleporterInteraction` (`SimpleBlockInteraction`); use is an ordinary block
interaction chain.

- Fails if the block has no `Teleporter`, the client is not ready yet, or the
  player already has `Teleport`, `PendingTeleport` or `UsedTeleporter`.
- On success: adds `Teleport` to the warp destination and
  `UsedTeleporter(world, position, clearoutXZ = 1.3, clearoutY = 2.5)`; no
  teleporter works again until the player moves > 1.3 blocks XZ or > 2.5 Y from
  the arrival point.
- The client receives [[ClientTeleport]].
- Links are one-way (the block's own warp only).
- A teleporter not in state `default` is reset to its default variant on use.
