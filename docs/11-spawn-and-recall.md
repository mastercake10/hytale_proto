# Spawn points and position recall

## Spawn providers

Each world has a spawn provider (world config; falls back to the world's
default provider when unset). It resolves a spawn per player
(`getSpawnPointAsync(world, uuid)`) and also exposes its full list
(`getSpawnPoints()`).

| Provider | Per-player spawn |
|----------|------------------|
| `GlobalSpawnProvider`         | One fixed point for everyone |
| `IndividualSpawnProvider`     | `spawnPoints[floorMod(hashUuid(uuid), spawnPoints.length)]`: stable per player, may differ between players |
| `FitToHeightMapSpawnProvider` | Wraps another provider. If the point's Y is `-2147483648` (unresolved), Y becomes heightmap height + 1 at that column (1 if no heightmap) |

## Spawn command

| Command | Permission | Effect |
|---------|------------|--------|
| `/spawn`                    | `spawn.self`  | Teleport to the per-player spawn |
| `/spawn <index>`            | `spawn.self`  | Teleport to `getSpawnPoints()[index]` |
| `/spawn <player> [index]`   | `spawn.other` | Same, for another player |
| `/spawn set [pos] [rot]`    | world editor group | Replace the provider with a `GlobalSpawnProvider` at `pos` (default: sender position) and `rot` (default: sender head rotation) |
| `/spawn default`            | `hytale:Admin` group | Clear the provider; the world default applies |

- An index out of range, or a point with unresolved Y (`-2147483648`), is
  rejected.
- `/spawn` and `/spawn <index>` can give different points: the per-player
  point is hashed, the index is used directly.
- Before teleporting, the player's current position and rotation are appended
  to their teleport history.

## Spawn marker

The world map spawn marker uses the per-player spawn
(`getSpawnPointAsync`, 10 s resolve timeout), i.e. the same point as `/spawn`
without an index.
