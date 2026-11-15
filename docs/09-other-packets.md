# Other Packets

Packets that are known by ID but not described on another page yet.

```packets
3 | Ping | both | Keepalive
4 | Pong | both | Keepalive reply
5 | NetworkTick | client | High-volume timing packet
100 | SetClientId | client | Assigns the client network id
105 | ClientReady | server | Client chunk/gameplay readiness flags
111 | MouseInteraction | server | Mouse button and targeted block/entity
```

## Joining and client stage

The client uses stage-specific packet handlers. Display/UI packets, including
`UpdatePointDisplay` (518) and the trigger-volume overlay packets, are only
accepted while the client is in the Playing stage. Sending them during
`SettingUp` is rejected by the client.

`ClientReady` (105) is sent by the client during setup and reports chunk or
gameplay readiness flags. It does not by itself mean the client has switched
to Playing.

The server-side join sequence is:

```text
JoinWorld (104)
  -> client readiness
  -> ViewRadius (32)
  -> SetEntitySeed (160)
  -> SetClientId (100)
  -> SetTimeDilation (30)
  -> UpdateFeatures (31)
  -> world/client effects and gameplay config
  -> SetUpdateRate (29)
  -> time packets
  -> UpdateWorldMapSettings (240)
```

`JoinWorld` starts the world transfer. The later packets are written from
`World.onFinishPlayerJoining` after the client readiness future completes.
`SetClientId` is only emitted from that join path; `UpdateWorldMapSettings`
follows after world-map setup but may also be sent again when map settings
change. In observed traffic, `SetClientId` is the first unambiguous
join-complete marker.

## DisplayDebug (114)

Client-bound debug-shape draw request. Shapes are transient client-side
primitives in world space. There is no server-side acknowledgement.

```packet
bound: client
summary: Draw a debug shape (sphere, cube, cylinder, etc.)
columns: Offset | Field Name | Field Type | Null bit | Notes
0  | Null bits           | `u8`        |        | bit0 `matrix`, bit1 `frustum_projection`
1  | `shape`             | `u8`        |        | `DebugShape` value
2  | `color`             | `Vector3f`  |        | 3 × `f32`
14 | `time`              | `f32`       |        | Lifetime in seconds
18 | `flags`             | `u8`        |        | `DebugFlags` bitmask
19 | `opacity`           | `f32`       |        |
23 | `matrix` offset     | `i32`       |        | Relative to variable block at byte 31; `-1` absent
27 | `frustum_projection` offset | `i32` |       | Relative to variable block at byte 31; `-1` absent
```

Variable block starts at byte 31. Each present array is a VarInt element count
followed by that many `f32` values.

`matrix` is 16 floats in row-major order, matching
`Matrix4dUtil.asFloatData`:

```text
m00 m01 m02 m03
m10 m11 m12 m13
m20 m21 m22 m23
m30 m31 m32 m33
```

A translation matrix therefore places the translation in `m30`, `m31`, `m32`
(the last row in this layout). `frustum_projection` is also used as the
shape-parameter array for disc, donut and sector shapes.

`DebugShape`:

```text
0 Sphere
1 Cylinder
2 Cone
3 Cube
4 Frustum
5 Sector
6 Disc
7 Donut
```

`DebugFlags`:

```text
1 Fade          fade the shape out over its lifetime
2 NoWireframe   do not draw the wireframe outline
4 NoSolid       do not draw the solid surface
```

Flags combine with bitwise OR, so `4` gives a wireframe-only cube.

Observed client behavior: these shapes are depth-tested. Solid and wireframe
shapes are hidden by blocks at distance. See [Markers and
overlays](10-marker-overlays.md).

## ClearDebugShapes (115)

Client-bound request with an empty body. It clears the client's debug shapes;
there is no per-shape removal packet.

```packet
bound: client
summary: Clear all client debug shapes
```
