# Markers and Overlays

Client-bound, visual-only packets for editor markers, trigger-volume display
and debug overlays. The client sends no acknowledgement. They are accepted
only in the client's Playing stage; see
[Joining and client stage](09-other-packets.md#joining-and-client-stage).

## Client rendering

| Overlay | Visible through terrain |
|---------|-------------------------|
| Point marker (`PointDisplayEntry`) | Yes |
| Trigger-volume box | No |
| [[BuilderToolLaserPointer]] beam | No (depth-tested) |
| [[DisplayDebug]] shape | No (depth-tested, any flags) |

![Point marker, trigger-volume box and laser-pointer box in a row](images/point-volume-laser-row.png)

Left to right: point marker, trigger-volume box, laser-pointer box.

## PointDisplayEntry

```text
0   null bits     u8         bit0 name, bit1 tags
1   position      Vector3f
13  rotation      Vector3f
25  shape         u8         PointShapeType: 0 Block, 1 Sphere
26  id offset     i32        relative to variable block at byte 38
30  name offset   i32        -1 absent
34  tags offset   i32        -1 absent
38  variable block
```

- `id`: VarString, required, non-empty, unique within the set. Entries with an
  empty id are not rendered.
- `name`: optional VarString label; if absent the label is `id`.
- `tags`: optional dictionary, VarInt count + key/value VarString pairs.
- `Block` renders a translucent block-sized volume with the label floating
  above it.

## UpdatePointDisplay (518)

```packet
bound: client
summary: Replace all point markers
columns: Offset | Field Name | Field Type | Null bit | Notes
0 | Null bits | `u8` | | bit0 `points`
```

Variable block at byte 1: VarInt count + `PointDisplayEntry[]`. Absent array
clears all markers.

## AddOrUpdatePointDisplay (519)

```packet
bound: client
summary: Add or update one point marker
columns: Offset | Field Name | Field Type | Notes
0 | `pointId` offset | `i32` | Relative to variable block at byte 8
4 | `entry` offset   | `i32` | Relative to variable block at byte 8
```

Variable block at byte 8: `pointId` VarString, then one `PointDisplayEntry`.
Replaces any marker with the same id.

## RemovePointDisplay (520)

```packet
bound: client
summary: Remove one point marker
```

Body: one VarString `pointId`.

## TriggerVolumeDisplayEntry

```text
0   null bits             u8        bit0 name, bit1 groupId, bit2 effectAssetRef
1   shapeType             u8        0 Box, 1 Sphere, 2 Cylinder
2   position              Vector3f  centre
14  dimensions            Vector3f  see below
26  color                 Vector3f
38  opacity               f32
42  groupColor            i32
46  targetTypes           u8        bitmask: 1 Player, 2 NPC, 4 Item drop, 8 Projectile
47  bool bits             u8        bit0 keepLoaded, bit1 cancelDelayedOnExit
48  cooldown              f32
52  cooldownMode          u8        0 Per entity, 1 Total
53  activationDelay       f32
57  conditionTiming       u8        0 Before volume delay, 1 After volume delay
58  rotation              Vector3f
70  volumeId offset       i32       required VarString
74  name offset           i32       -1 absent
78  groupId offset        i32       -1 absent
82  effectAssetRef offset i32       -1 absent
86  variable block
```

Offsets are relative to byte 86; strings are written in field order.

`dimensions` by shape: Box = half-extents; Sphere = `x` radius; Cylinder =
`x` radius, `y` height.

## UpdateTriggerVolumeDisplay (470)

```packet
bound: client
summary: Replace all trigger-volume overlays
columns: Offset | Field Name | Field Type | Null bit | Notes
0 | Null bits | `u8` | | bit0 `volumes`
```

Variable block at byte 1: VarInt count + `TriggerVolumeDisplayEntry[]`.
Absent array clears all overlays.

## AddOrUpdateTriggerVolumeDisplay (471)

```packet
bound: client
summary: Add or update one trigger-volume overlay
columns: Offset | Field Name | Field Type | Notes
0 | `volumeId` offset | `i32` | Relative to variable block at byte 8
4 | `entry` offset    | `i32` | Relative to variable block at byte 8
```

Variable block at byte 8: `volumeId` VarString, then one
`TriggerVolumeDisplayEntry`. Replaces any overlay with the same id.

## RemoveTriggerVolumeDisplay (472)

```packet
bound: client
summary: Remove one trigger-volume overlay
```

Body: one VarString `volumeId`.

## BuilderToolLaserPointer (419)

Timed laser segment between two world-space points.

```packet
bound: client
summary: Timed laser-pointer segment
columns: Offset | Field Name | Field Type | Notes
0  | `playerNetworkId` | `i32`
4  | `startX`          | `f32`
8  | `startY`          | `f32`
12 | `startZ`          | `f32`
16 | `endX`            | `f32`
20 | `endY`            | `f32`
24 | `endZ`            | `f32`
28 | `color`           | `i32` | RGB integer
32 | `durationMs`      | `i32`
```
