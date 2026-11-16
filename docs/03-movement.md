# Movement and Timing

## ClientMovement (108)

Clients send movement frequently, including while mostly stationary. The packet
can carry an absolute position, a relative delta, or both. A movement packet may
also carry an acknowledgement for a server-issued transform update.

Layout (fixed size: 117 bytes):

```packet
bound: server
summary: Position, velocity, movement states, ack
columns: Offset | Field Name | Field Type | Null bit | Notes
0   | Null bits               | `u8`                |               | Optional-field presence
1   | Null bits 2             | `u8`                |               | bit0 `rider_movement_states`
2   | `movement_states`       | `MovementStates`    | byte 0, bit 0 | 4 bytes
6   | `relative_position`     | `HalfFloatPosition` | byte 0, bit 1 | 3 × `f16`
12  | `absolute_position`     | `Position`          | byte 0, bit 2 | 3 × `f64`
36  | `body_orientation`      | `Direction`         | byte 0, bit 3 | 3 × `f32`
48  | `look_orientation`      | `Direction`         | byte 0, bit 4 | 3 × `f32`
60  | `teleport_ack`          | `TeleportAck`       | byte 0, bit 5 | 1-byte teleport id
61  | `wish_movement`         | `Position`          | byte 0, bit 6 | 3 × `f64`
85  | `velocity`              | `Vector3d`          | byte 0, bit 7 | 3 × `f64`
109 | `mounted_to`            | `i32`               |               | Always present
113 | `rider_movement_states` | `MovementStates`    | byte 1, bit 0 | 4 bytes
```

Null bits are two bytes at the start of the fixed block. Absent optional fields
are written as zero bytes with their null bit cleared. `mounted_to` is not
optional.

## ClientTeleport (109)

Server-directed transform update. Fixed size: 55 bytes; there is no variable
block.

```packet
bound: client
summary: Server-directed transform update
columns: Offset | Field Name | Field Type | Notes
0  | `teleport_id`               | `u8`             | Acknowledged by the client in `ClientMovement`
1  | `ignored_transform_fields`  | `i16`            | Bitmask
3  | `relative_transform_fields` | `i16`            | Bitmask
5  | `model_transform`           | `ModelTransform` | 49 bytes
54 | `reset_velocity`            | `bool`
```

`ModelTransform` is a 49-byte structure containing position, body orientation
and look orientation.

Observed server behavior:

- The server tracks a queue of issued transform ids.
- An acknowledgement must match an outstanding id.
- An unmatched acknowledgement can be treated as invalid.
- The id is only one byte in the acknowledgement path, so wraparound and
  multiple outstanding requests need care.
- The queue is strict FIFO on the wire id: an acknowledgement is validated
  against the head of the queue.
- While the queue is non-empty, movement packets without an acknowledgement
  can be discarded instead of applied. Movement immediately after a server
  teleport is therefore unreliable until that teleport has been acknowledged.

## Pause state

```packets
158 | SetPaused | server | Client pause state (single `bool`)
159 | ServerSetPaused | client | Server pause state (single `bool`)
```

- Movement and interaction processing can be suspended while paused.
- Both packets contain a single boolean byte.

## Rejected positions

`INVALID_POSITION` in a disconnect reason indicates the server rejected a
position update rather than simply ignoring it.
