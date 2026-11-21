# Other Packets

Packets not covered on another page.

```packets
3 | Ping | client | Keepalive / latency probe
4 | Pong | server | Reply to Ping
5 | NetworkTick | client | Tick duration and server tick number
100 | SetClientId | client | Assigns the client's network entity id
105 | ClientReady | server | Client chunk/gameplay readiness flags
111 | MouseInteraction | server | Mouse button and targeted block/entity
2 | ServerDisconnect | client | Disconnect with type and optional reason
```

Fixed layouts (no variable block unless noted):

| Packet | Layout |
|--------|--------|
| Ping (28 B) | `id` i32 @0, `time` InstantData @4 (`seconds` i64, `nanos` i32), `lastPingValueRaw` i32 @16, `lastPingValueDirect` i32 @20, `lastPingValueTick` i32 @24 |
| Pong (19 B) | `id` i32 @0, `time` InstantData @4, `type` u8 @16 (`0` Raw, `1` Direct, `2` Tick), `packetQueueSize` i16 @17 |
| NetworkTick (8 B) | `tickDurationMicros` i32 @0, `serverTick` i32 @4 |
| SetClientId (4 B) | `clientId` i32 @0 |
| ClientReady (1 B) | bool bits: bit0 `readyForChunks`, bit1 `readyForGameplay` |
| ServerDisconnect | null bits u8 @0 (bit0 `reason`), `type` u8 @1 (`0` Disconnect, `1` Crash); variable block @2: [FormattedMessage](06-interface-pages.md#formattedmessage) `reason` |

MouseInteraction layout: `?` (fixed block 44 B, variable block at 52).

## Joining and client stage

The client accepts display/UI packets (including [[UpdatePointDisplay]] and
the trigger-volume overlay packets) only in its Playing stage; they are
rejected during `SettingUp`.

Server join sequence:

1. `JoinWorld` (104) starts the world transfer.
2. The server waits for both: the spawn chunk loaded, and `ClientReady` with
   `readyForChunks = 1, readyForGameplay = 0` (timeout 30 s, then the join fails).
3. The server then sends, in order: `ViewRadius` (32, value = max view radius
   in chunks x 32), `SetEntitySeed` (160), `SetClientId` (100),
   `SetTimeDilation` (30), `UpdateFeatures` (31), sun settings, post-FX
   settings, gameplay config, `SetUpdateRate` (29), time packets,
   `UpdateWorldMapSettings` (240).

`SetClientId` is sent only by this sequence, so it marks join completion.
`UpdateWorldMapSettings` is also re-sent when map settings change.
`ClientReady` alone does not mean the client is in Playing.

On `ClientReady` with `readyForGameplay = 1`, a player still waiting for
client-ready is sent a teleport to its current position.

## DisplayDebug (114)

Draws a transient debug shape in world space. No acknowledgement.

```packet
bound: client
summary: Draw a debug shape (sphere, cube, cylinder, etc.)
columns: Offset | Field Name | Field Type | Null bit | Notes
0  | Null bits           | `u8`        |        | bit0 `matrix`, bit1 `frustum_projection`
1  | `shape`             | `u8`        |        | `DebugShape`
2  | `color`             | `Vector3f`  |        | 3 × `f32`
14 | `time`              | `f32`       |        | Lifetime in seconds
18 | `flags`             | `u8`        |        | `DebugFlags` bitmask
19 | `opacity`           | `f32`       |        |
23 | `matrix` offset     | `i32`       |        | Relative to variable block at byte 31; `-1` absent
27 | `frustum_projection` offset | `i32` |       | Relative to variable block at byte 31; `-1` absent
```

Each array: VarInt count + that many `f32`.

- `matrix`: 16 floats, row-major (`m00 m01 m02 m03 m10 ... m33`); translation
  is in `m30 m31 m32`.
- `frustum_projection`: also the shape-parameter array for Sector, Disc and
  Donut.

`DebugShape`: `0` Sphere, `1` Cylinder, `2` Cone, `3` Cube, `4` Frustum,
`5` Sector, `6` Disc, `7` Donut.

`DebugFlags` (OR-combined; other bits undefined):

| Bit | Name | Effect |
|----:|------|--------|
| 1 | Fade        | Fade out over lifetime |
| 2 | NoWireframe | No wireframe outline |
| 4 | NoSolid     | No solid surface (`4` alone = wireframe only) |

Shapes are depth-tested (hidden behind blocks). See
[Markers and overlays](10-marker-overlays.md).

## ClearDebugShapes (115)

Empty body. Clears all debug shapes; there is no per-shape removal.

```packet
bound: client
summary: Clear all client debug shapes
```
