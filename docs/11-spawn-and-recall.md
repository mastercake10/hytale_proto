# Spawn points and position recall

How the server chooses a spawn position, and how it reacts when a player is
moved into chunks that are not loaded.

## Spawn providers

A world's spawn provider is an `ISpawnProvider` in the world config. It is
queried per player:

```text
getSpawnPointAsync(world, uuid) -> Transform
```

Known implementations:

- `GlobalSpawnProvider`: one fixed spawn point for every player.
- `IndividualSpawnProvider`: a list of spawn points; the index is
  `floorMod(hash(uuid), spawnPoints.length)`, so each player gets a stable but
  possibly different point.
- `FitToHeightMapSpawnProvider`: a configured position whose Y is adjusted to
  the local heightmap before use.

## Spawn command

`/spawn` (`SpawnCommand`) has an optional `spawnIndex` argument:

- With no index: `spawnProvider.getSpawnPointAsync(world, playerUuid)`.
- With an index: `spawnProvider.getSpawnPoints()[index]` is used directly.
  Out-of-range indices are rejected; a point whose Y equals
  `-2147483648` (unresolved) is also rejected.

The two forms can therefore disagree: the hashed per-player point and
`spawnPoints[0]` are not necessarily the same location.

`/spawn set` (world editor permission group) replaces the provider with a
`GlobalSpawnProvider` positioned at the given coordinates. Subsequent
`/spawn` calls for every player use that new single point.

## Spawn marker

The world map spawn marker resolves the same provider and therefore shows the
same position that `/spawn` would use for that player.

