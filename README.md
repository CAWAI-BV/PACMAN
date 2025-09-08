# Pac-Style Maze Chaser — Developer Spec Sheet (MVP)

A small, legally distinct “Pac‑style” maze chaser: player collects dots, avoids four enemies, uses power‑up to flip the odds. Designed for 1–2 weeks of work by a single dev.

## 1) High-Level Overview

Platforms: Desktop (Windows/macOS), keyboard input. Optional WebGL/HTML5 export after MVP.

Engine: Unity 2022 LTS or Godot 4.x (choose one). This spec lists engine-agnostic behaviors.

Camera: Orthographic, top-down.

Framerate: Fixed timestep with deterministic movement tied to grid.

Target Resolution: 1920×1080 (scale-independent, pixel-perfect). Tile size 16 px; maze grid 28×31 tiles (outer walls included).

Goal: Clear all dots; lose a life on enemy contact unless powered up. Game ends when all lives are lost or level is cleared.

## 2) Core Game Loop

Start Screen → Level loads with player + four enemies spawned.

Collect dots to increase score and progress toward level clear.

Avoid enemies; pick up power pellets to become empowered temporarily.

While empowered: enemies become frightened; touching them awards bonuses and sends them to respawn.

Level complete when all dots are eaten → either loop same map faster, or load next map (optional).

Lose life on enemy collision when not empowered → respawn sequence → continue until lives = 0.

## 3) World & Grid

Grid: 28 columns × 31 rows. Impassable wall tiles, traversable path tiles, and tunnels.

Tunnels: Left/right wrap to opposite edge. Movement speed reduced by 10% while inside tunnels.

Spawn Points:

Player: fixed start tile.

Enemy House: 3×2 room with a one‑tile doorway; enemies exit one at a time.

Dot Layout: ~240 small dots on path tiles; 4 power pellets near corners.

## 4) Player

Movement: Discrete grid navigation with buffered inputs.

Input buffer window: 150 ms to pre‑select a turn.

If next tile in pressed direction is blocked, continue moving current direction until a turn becomes possible.

Speed: 12 tiles/second (base). In frightened mode, enemies slow; player speed constant.

Collision: Axis‑aligned; collideable when occupying the same tile center ± 0.25 tile.

Lives: 3 (configurable). On death: brief pause (1.0 s), death anim (1.0 s), respawn (1.0 s).

## 5) Enemies (Ghosts)

Count: 4 enemies with distinct target behaviors (simple, readable AI).

States: IdleInHouse → ExitHouse → Scatter ↔ Chase → Frightened → Eaten → ReturnToHouse.

Global Mode Timer (per level):

Scatter 7 s → Chase 20 s → Scatter 7 s → Chase 20 s → Scatter 5 s → Chase (until level end).

Base Speed: 11 tiles/s (chase & scatter); Frightened Speed: 8 tiles/s; Tunnel Speed: 9 tiles/s.

Turning Rules: At intersections, choose next tile per behavior; cannot reverse direction unless global mode switches or entering/leaving frightened.

### 5.1 Enemy Targeting (Simple, clone‑friendly)

Red (Chaser): target player’s current tile.

Pink (Ambusher): target 2 tiles ahead of player’s current direction (clamped to nearest valid path).

Blue (Flanker): target the midpoint between player and Red’s tile, then project 2 tiles beyond the midpoint (approximate pincer). If invalid, fallback to shortest path to player.

Orange (Roamer): if farther than 8 tiles from player, target player; otherwise target its scatter corner.

### 5.2 Pathfinding

Grid‑based shortest path with BFS (cost = 1 per tile). Break ties with Left > Up > Right > Down priority to create consistent personality.

### 5.3 Frightened & Eaten

Trigger: Player eats power pellet.

Frightened Duration: 6.0 s at Level 1; minus 0.5 s each subsequent level to a floor of 2.0 s.

Behavior: Move away from player by choosing the longest of available next steps (greedy one‑step lookahead) and randomize tie breaks.

On Capture: Enemy becomes Eaten (eyes only), speed 15 tiles/s, returns to house via shortest path; after 1.0 s in house, rejoin flow.

## 6) Dots & Power Pellets

Small Dot: 10 pts, pickup radius 0.4 tile.

Power Pellet: 50 pts, triggers frightened; blinking visual for last 1.5 s.

Enemy Capture Chain: 200, 400, 800, 1600 pts resets after power ends.

Dot‑Eaten SFX Cooldown: 60 ms to avoid audio spam.

## 7) Scoring & Progression

Small Dot: +10

Power Pellet: +50

Fruit (optional MVP+1): spawns twice per level at dot thresholds (e.g., 70% and 30% remaining); value 100–500. Lifetime 9 s.

Extra Life (optional): at 10,000 pts.

HUD: Score (left), High Score (center), Lives (right). Level indicator via small icons or stage number.

## 8) Controls (Desktop)

Arrow Keys / WASD: Move.

P / Esc: Pause/Unpause.

Enter/Space: Confirm on menus.

## 9) Game States & Flow

Boot → Main Menu → Level Intro → Gameplay → (Pause) → Life Lost → Respawn → (Win | Game Over) → High Score Entry → Main Menu.

Level Intro: 2.0 s camera idle; enemies bounce inside house; “READY!” text.

Pause: Freeze updates; dim screen; show menu overlay.

## 10) UI/UX

Pixel‑clean rendering: snap sprites to grid; no sub‑pixel movement.

Readability: distinct colors for enemies; frightened = blue + white blink.

Feedback:

Dot pickup sound each Nth dot (see cooldown).

Power pellet: bassy whoosh + screen vignette pulse.

Capture: ascending pitch per chain step.

Accessibility:

Color‑blind friendly palettes; ensure frightened vs normal is readable via shape/brightness, not only hue.

Remappable keys (JSON settings file).

## 11) Art & Audio (Legally Safe)

Style: Retro pixel art, original assets (no trademark shapes or exact ghost looks). Use geometric walls, simple character shapes.

Sprites:

Player: 16×16, two‑frame “chomp” per direction.

Enemy: 16×16, two‑frame walk per direction; separate frightened and eyes sprites.

Dots: 4×4; Power Pellet: 8×8.

Fruit (opt): 16×16.

Tileset: Walls, corners, T‑junctions, tunnel entrances; 16×16.

FX: Original SFX for dot, power, capture, death; short looped BGM.

