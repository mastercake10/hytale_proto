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

Client side of the setup stage (after authentication):

1. Server sends `WorldSettings` (20) and `ServerInfo` (223).
2. Client sends `RequestAssets` (23), a compressed packet (zstd body) holding
   the list of common assets it lacks; an empty, non-null list is valid. A
   second `RequestAssets` is a protocol error.
3. Client may send `ViewRadius` (32, `i32` blocks; the server uses
   `ceil(value / 32)` chunks).
4. Server sends the asset registries, translations, `WorldLoadProgress` and
   `WorldLoadFinished` (22).
5. Client sends `SetupFinalize` (33, empty). Before `RequestAssets` it is a
   protocol error.

Every setup stage and the play stage have server-side timeouts; in play, a
client that sends nothing is disconnected, so `Pong` replies (one per
`PongType`) keep an otherwise idle connection alive.

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

## Server player list

The tab list. A UUID is 16 bytes: most significant half, then least
significant half, each a **big-endian** `i64` (unlike the little-endian
integers elsewhere).

### AddToServerPlayerList (224)

```packet
bound: client
summary: Add players to the server player list
columns: Offset | Field Name | Field Type | Notes
0 | `players` | ServerPlayerListPlayer[] | `VarInt` count + entries
```

`ServerPlayerListPlayer`, fixed block 42 bytes, variable block at 42:

| Offset | Field Name | Field Type | Null bit | Notes |
|-------:|------------|------------|----------|-------|
| 0  | Null bits         | `u8`     |      | bit0 `worldUuid`, bit1 `livesRemaining`, bit2 `username` |
| 1  | `uuid`            | UUID     |      | Player UUID |
| 17 | `worldUuid`       | UUID     | bit0 | Zero-filled when absent |
| 33 | `ping`            | `i32`    |      | |
| 37 | `spectating`      | `bool`   |      | |
| 38 | `livesRemaining`  | `i32`    | bit1 | Zero-filled when absent |
| 42 | `username`        | `VarString` | bit2 | Only variable field, starts at 42 |

### RemoveFromServerPlayerList (225)

```packet
bound: client
summary: Remove players from the server player list
columns: Offset | Field Name | Field Type | Notes
0 | `players` | UUID[] | `VarInt` count + 16-byte UUIDs
```

### UpdateServerPlayerList (226)

```packet
bound: client
summary: Move listed players to another world
columns: Offset | Field Name | Field Type | Notes
0 | `players` | ServerPlayerListUpdate[] | `VarInt` count + 32-byte entries: `uuid` UUID @0, `worldUuid` UUID @16
```

### UpdateServerPlayerListPing (227)

```packet
bound: client
summary: Ping values of listed players
columns: Offset | Field Name | Field Type | Notes
0 | `players` | Map<UUID, i32> | `VarInt` count + entries: UUID (16 B), `i32` ping
```

## Player identity

Entity records in `EntityUpdates` (161) carry only the network id; no
component holds the player's UUID. The `Nameplate` component (type 0) holds the
displayed name as `text`. UUID and username appear together only in
[[AddToServerPlayerList]] entries. World map player markers
(`PlayerMarkerComponent`) carry `playerId` (UUID) when the server shows
players on the map. Matching a player entity to its UUID therefore goes
through the name.
