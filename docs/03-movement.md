# Movement and Timing

## ClientMovement (108)

Sent continuously by the client. Fixed size 117 bytes, no variable block.
Absent optional fields are zero-filled.

```packet
bound: server
summary: Position, velocity, movement states, ack
columns: Offset | Field Name | Field Type | Null bit | Notes
0   | Null bits               | `u8`                |               |
1   | Null bits 2             | `u8`                |               |
2   | `movement_states`       | `MovementStates`    | byte 0, bit 0 | 4 bytes
6   | `relative_position`     | `HalfFloatPosition` | byte 0, bit 1 | Delta, 3 × `i16` / 10000 blocks
12  | `absolute_position`     | `Position`          | byte 0, bit 2 |
36  | `body_orientation`      | `Direction`         | byte 0, bit 3 |
48  | `look_orientation`      | `Direction`         | byte 0, bit 4 |
60  | `teleport_ack`          | `u8`                | byte 0, bit 5 | Teleport id
61  | `wish_movement`         | `Position`          | byte 0, bit 6 |
85  | `velocity`              | `Vector3d`          | byte 0, bit 7 |
109 | `mounted_to`            | `i32`               |               | Always present; 0 = not mounted
113 | `rider_movement_states` | `MovementStates`    | byte 1, bit 0 | 4 bytes
```

Server handling:

- Non-finite (NaN/Inf) `absolute_position` or orientation is a disconnect.
- `teleport_ack` requires `absolute_position`; see [Teleport acknowledgement](#teleport-acknowledgement).
- Ignored until the client is ready (see
  [Joining and client stage](09-other-packets.md#joining-and-client-stage)).
- `movement_states` and `velocity` are always applied. Everything else is
  dropped while a teleport is unacknowledged.
- Rider states, orientation, wish movement and position are applied only when
  `mounted_to` matches the server's mount id for the player.
- `absolute_position` takes precedence; `relative_position` is used only when
  no absolute position is sent.
- `movement_states` replaces the server's whole state set; when absent the
  last received states stay in effect. A zero `relative_position` still
  queues a (null) relative move when `movement_states` is present.

### MovementStates (4 bytes)

| Byte | Bits (1, 2, 4, 8, 16, 32, 64, 128) |
|------|-------------------------------------|
| 0 | idle, horizontalIdle, jumping, flying, walking, running, sprinting, crouching |
| 1 | forcedCrouching, falling, fallingFar, climbing, inFluid, swimming, swimJumping, onGround |
| 2 | mantling, sliding, mounting, rolling, sitting, gliding, sleeping, (unused) |
| 3 | extraJumpsUsed (`u8`) |

Server-side effects of `crouching` (also `sliding`; bounding box also
`forcedCrouching`): the model's crouch bounding box is used and the eye height
drops by the model's `CrouchOffset` (player: 1.6 - 0.4 = 1.2). The eye height
feeds the interaction-range check (eye to target <= `UseDistance` + 2).
No movement-speed validation reads it. NPC hearing ignores crouching players
(see [NPC detection](12-npc-detection.md)).

## ClientTeleport (109)

Server-set transform. Fixed size 55 bytes.

```packet
bound: client
summary: Server-directed transform update
columns: Offset | Field Name | Field Type | Notes
0  | `teleport_id`               | `u8`             | Echoed in `ClientMovement.teleport_ack`
1  | `ignored_transform_fields`  | `i16`            | Bitmask, see below
3  | `relative_transform_fields` | `i16`            | Bitmask; server sends 0
5  | `model_transform`           | `ModelTransform` | 49 bytes
54 | `reset_velocity`            | `bool`
```

`ModelTransform` (49 bytes): `u8` null bits (bit0 position, bit1 body,
bit2 look), `Position` at 1, body `Direction` at 25, look `Direction` at 37.

`ignored_transform_fields` bits (set = keep the client's current value):

| Bit | Field | Bit | Field | Bit | Field |
|-----|-------|-----|-------|-----|-------|
| 0 | position x | 3 | body yaw   | 6 | look yaw   |
| 1 | position y | 4 | body pitch | 7 | look pitch |
| 2 | position z | 5 | body roll  | 8 | look roll  |

## Teleport acknowledgement

- Each `ClientTeleport` appends `(id, target position)` to a per-player FIFO
  queue. Ids increment per teleport; the wire id is the low 8 bits.
- An ack is checked against the queue head only:
  - queue empty or `ack != head.id & 0xFF` → disconnect
    (`incorrectTeleportId`);
  - `absolute_position` farther from the target than
    `sqrt(0.001) + half-float precision of the target` → disconnect
    (`invalidTeleport`);
  - otherwise the head is removed.
- While the queue is not empty, movement other than states and velocity is
  dropped (see [[ClientMovement]]). The teleport completes on the movement
  that empties the queue.

## Disconnect reasons

| Translation key (`server.general.disconnect.*`) | Cause |
|---|---|
| `impossiblePosition`    | Non-finite `absolute_position` |
| `impossibleOrientation` | Non-finite body or look orientation |
| `invalidTeleport`       | Ack without `absolute_position`, or ack position off target |
| `incorrectTeleportId`   | Ack id does not match queue head |

## Pause state

```packets
158 | SetPaused | server | Client pause request (single `bool`)
159 | ServerSetPaused | client | World pause state (single `bool`)
```

`SetPaused` is honoured only on a singleplayer server with exactly one player
in the world. When the world's pause state changes, the server broadcasts
`ServerSetPaused` to all players in it.
