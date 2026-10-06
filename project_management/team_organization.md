# Team Organization

Team of two: **obakri: oumaima bakri** and **rhssayn: redouane hssayn**.

## Who did what

### oumaima — Gameplay, systems and tooling

- Config parsing and validation (`Parser`), JSON-with-comments support, maze-dimension and key validation.
- Maze generator integration (`Level`), adapting our loader to the assigned `A-Maze-ing` package without modifying it.
- Core gameplay: player movement, collisions, lives, level timer, multi-level progression, win/lose states.
- Ghost AI: Blinky (BFS chase), Clyde (chase/retreat heuristic), Pinky (ambush-ahead targeting), Inky (vector-based targeting), shared `GhostState` machine (Normal / Frightened / Eaten).
- Smooth movement and sprite animation for both players and ghosts.
- Highscore system, name entry, pause, two-player co-op with shared lives, key-and-door mechanic, cheat mode (god mode, ghost freeze, level skip, invisible mode).
- README, and project management documentation.

### redouane — Design, UI and media

- Visual identity: color palette, theme, consistent look across every screen.
- UI implementation: main menu carousel, header/footer, dialogue box, back-to-menu control.
- Screens: scoreboard, sound settings, single- and two-player skin selector, instructions/info page.
- Sprite sheets and icons: ghosts, player skins, gums, HUD elements; animated video background and theme switching.
- Audio: music, sound effects, volume controls.
- linting/mypy/flake8 fixes, Makefile

## How decisions were made

We split ownership by layer early on: gameplay/logic/tooling on one side, UI/visual/audio on the other, meeting to integrate the two whenever a feature touched both (e.g. a new cheat needing both logic and an on-screen indicator). Technical decisions inside each person's area were made independently and explained to the other afterward rather than debated in advance, to keep velocity up; cross-cutting decisions (anything both of us would need to build against, like the `GameState` interface, sprite-frame data shape, or the config file format) were discussed together before implementation started.

Notable decisions and the reasoning behind them:

| Decision | Reasoning |
|---|---|
| Greedy, one-tile-lookahead ghost movement instead of full BFS pathfinding | Matches the original arcade AI's behavior and keeps each ghost's personality distinct; BFS gives all ghosts identical "perfect" pathing and removes the quirks that make them feel different. |
| Pacgums stored as plain position data (sets/dicts), not entity objects | Hundreds of gums per level; giving each one a full class with an `update()` method is unnecessary overhead for something that never acts, only gets eaten. |
| `GameState` owns all rules; the renderer only reads and draws | Keeps gameplay logic testable and independent of `pygame`, and avoids the renderer silently deciding scoring/collision outcomes. |
| Shared lives pool for two-player co-op, not per-player lives | The two players are on the same team; independent lives would let one player's risk be meaningless to the other. |
| JSON highscore file capped at top 10, sorted with `bisect.insort_left` | Matches the subject's requirement directly; the list never exceeds 10 items so correctness and simplicity mattered more than optimizing for a growing dataset. |

## How issues and blocking points were handled

When one of us hit a blocker, the default was to debug it together rather than work around it silently, since several of these bugs touched both layers, for example, a ghost-position bug could look like a rendering issue until traced back to game logic. Bugs were tracked informally as they were found and fixed in the same session where possible; the acceptance test document lists the ones that mattered.

Technical disagreements (for example, how aggressively ghosts should path toward the player) were resolved by testing both options briefly and picking whichever felt closer to the original game's behavior, rather than by argument.
