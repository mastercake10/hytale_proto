# NPC detection

How hostile NPCs notice and drop a player (server NPC roles and the
`server/npc` sensor code). Distances are 3D; view sectors are horizontal (x/z)
only.

## Attitude

Order: temporary override → same spawn lineage (friendly) → attitude group map
→ role `DefaultPlayerAttitude` (default **Hostile**). Damaging an NPC sets a
Hostile override for 60 s; being seen during a chase, 120 s.

A player that is Intangible, spectating or in Creative is not detectable.
Invulnerability does not matter.

## Sensors (standard detection)

Any one triggers:

| Check | Range | Line of sight | Notes |
|-------|-------|---------------|-------|
| Absolute | role value, 2–4 | no | through walls |
| Sight | `ViewRange`, 12–24 | yes | inside `ViewSector` (0 = all directions) |
| Hearing | `HearingRange`, usually 8 | no | skipped while the player **crouches** |

- Crouching is the client's `MovementStates` crouch flag.
- Line of sight: ray from NPC eye to player eye; air and `Transparent`
  blocks pass, any other block hitbox blocks; an unloaded section blocks.
- No general block-break or footstep noise. Block events (damage,
  destruction, interaction) are used by specific roles only (spiders: damaged
  webs within 10; trorks: their chests).
- No rule depends on the blocks under the player; altitude filters ignore
  players.
- Once alerted, the target is kept while visible within `AlertedRange`
  (20–50) or heard within `HearingRange`.

## Losing the target

- Not seen and not heard: confused 1–2 s, then search ~10–14 s.
- Path failure 5 s → unreachable (idle or return home).
- Melee "intelligent" NPCs give up after 5 s when the target is out of attack
  distance and more than ±2 blocks higher or lower.
- Leash: default 30 (hard 160); intelligent roles 45 (hard 200). Returning
  home heals the NPC.
- Sleeping roles (awake 6:01–17:59 by default) notice only hearing range or
  damage at night; skeleton soldier/knight/fighter/archer never sleep.

## Common roles

| Role | Attack | View / sector | Hearing | Absolute | Attack distance |
|------|--------|---------------|---------|----------|-----------------|
| Skeleton | melee | 15 / 180° | 8 | 2 | 2 |
| Skeleton soldier, knight | melee | 15 / 270° | 8 | 2 | 3 |
| Skeleton archer, ranger, scout, mage | ranged | 15 / 270° | 8 | 2 | 15 |
| Zombie | melee | 12 / 120° | 8 | 4 | 2 |
| Spider | melee | 16 / 180° | 8 | 4 | 2.5 |
| Goblin scrapper, miner | melee | 12 / 160° | 8 | 2 | 2.5–3 |
| Goblin lobber | ranged | 15 / 160° | 8 | 2 | 12 |
| Trork hunter, guard | ranged | 20, all directions, needs sight | – | 2 | 12 |

All attacks need line of sight within attack distance.
