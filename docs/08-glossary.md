# Protocol Glossary

Shared enums. All are encoded as `u8` unless the using packet says otherwise.

## SetGameMode (101)

```packet
bound: client
summary: One byte: 0 adventure, 1 creative
Game mode | `u8` | `0` Adventure, `1` Creative
```

## Movement directions

| Value | Name | Value | Name |
|------:|------|------:|------|
| 0 | None    | 5 | ForwardLeft  |
| 1 | Forward | 6 | ForwardRight |
| 2 | Back    | 7 | BackLeft     |
| 3 | Left    | 8 | BackRight    |
| 4 | Right   |   |              |

## Block faces

| Value | Name | Value | Name |
|------:|------|------:|------|
| 0 | None  | 4 | South |
| 1 | Up    | 5 | East  |
| 2 | Down  | 6 | West  |
| 3 | North |   |       |

## Rotations

`0` None, `1` Ninety, `2` OneEighty, `3` TwoSeventy.

## Apply-force states

`0` Waiting, `1` Ground, `2` Collision, `3` Timer.

## Page ids

Used by [[SetPage]].

| Value | Name | Value | Name |
|------:|------|------:|------|
| 0 | None            | 7  | Custom         |
| 1 | Bench           | 8  | Serverside     |
| 2 | Inventory       | 9  | Chapters       |
| 3 | ToolsSettings   | 10 | ChapterRewards |
| 4 | Map             | 11 | PortalSummon   |
| 5 | MachinimaEditor | 12 | PortalActive   |
| 6 | ContentCreation | 13 | PortalError    |

Custom pages ([[CustomPage]]) are identified by a key string, not by this id.

## Chunk sentinel

Height `-2147483648` (`i32` min) in [[SetColumn]] means void/unknown.
