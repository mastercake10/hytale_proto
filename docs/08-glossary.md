# Protocol Glossary

## SetGameMode (101)

```packet
bound: client
summary: One byte: 0 adventure, 1 creative
Game mode | `u8` | See table below
```

| Value | Game mode |
|------:|-----------|
|     0 | Adventure |
|     1 | Creative  |

## Movement directions

| Value | Name         |
|------:|--------------|
|     0 | None         |
|     1 | Forward      |
|     2 | Back         |
|     3 | Left         |
|     4 | Right        |
|     5 | ForwardLeft  |
|     6 | ForwardRight |
|     7 | BackLeft     |
|     8 | BackRight    |

## Block faces

| Value | Name  |
|------:|-------|
|     0 | None  |
|     1 | Up    |
|     2 | Down  |
|     3 | North |
|     4 | South |
|     5 | East  |
|     6 | West  |

## Rotations

| Value | Name       |
|------:|------------|
|     0 | None       |
|     1 | Ninety     |
|     2 | OneEighty  |
|     3 | TwoSeventy |

## Apply-force states

| Value | Name      |
|------:|-----------|
|     0 | Waiting   |
|     1 | Ground    |
|     2 | Collision |
|     3 | Timer     |

## Page ids

| Value | Name |
|------:|------|
|     0 | None |

Page ids beyond `None` are defined by the server UI implementation; custom pages
are usually identified by their key string rather than the numeric page id.

## Chunk sentinel

Height value `-2147483648` means void/unknown in
[[SetColumn]] data.
