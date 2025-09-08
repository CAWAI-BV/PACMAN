import pygame
import random
from collections import deque

# Constants
TILE_SIZE = 32
LEVEL = [
    "###############",
    "#.............#",
    "#.###.###.###.#",
    "#o###.###.###o#",
    "#.............#",
    "#.###.###.###.#",
    "#...#.....#...#",
    "###.#.###.#.###",
    "#...#.#.#.#...#",
    "#.###.#.#.###.#",
    "#.............#",
    "###############",
]
WIDTH = len(LEVEL[0]) * TILE_SIZE
HEIGHT = len(LEVEL) * TILE_SIZE
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 100, 150)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)


class Board:
    def __init__(self):
        self.walls = []
        self.dots = set()
        self.power = set()
        for r, row in enumerate(LEVEL):
            for c, ch in enumerate(row):
                if ch == '#':
                    self.walls.append(pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif ch == '.':
                    self.dots.add((c, r))
                elif ch == 'o':
                    self.power.add((c, r))

    def draw(self, surf):
        for rect in self.walls:
            pygame.draw.rect(surf, BLUE, rect)
        for (c, r) in self.dots:
            pygame.draw.circle(surf, WHITE, (c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2), 4)
        for (c, r) in self.power:
            pygame.draw.circle(surf, WHITE, (c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2), 8)

    def is_wall(self, c, r):
        if r < 0 or r >= len(LEVEL) or c < 0 or c >= len(LEVEL[0]):
            return True
        return LEVEL[r][c] == '#'


class Entity:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.dir = (0, 0)
        self.speed = 2
        self.color = color

    def pixel_pos(self):
        return int(self.x), int(self.y)

    def tile_pos(self):
        return int(self.x // TILE_SIZE), int(self.y // TILE_SIZE)

    def move(self):
        self.x += self.dir[0] * self.speed
        self.y += self.dir[1] * self.speed

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x) + TILE_SIZE // 2, int(self.y) + TILE_SIZE // 2), TILE_SIZE // 2 - 2)


class Pacman(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, ORANGE)
        self.lives = 3
        self.score = 0
        self.next_dir = (0, 0)

    def update(self, board):
        if self.next_dir != self.dir:
            if self.can_move(board, self.next_dir):
                self.dir = self.next_dir
        if not self.can_move(board, self.dir):
            return
        self.move()
        tile = self.tile_pos()
        if tile in board.dots:
            board.dots.remove(tile)
            self.score += 10
        if tile in board.power:
            board.power.remove(tile)
            self.score += 50
            return True
        return False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.next_dir = (-1, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.next_dir = (1, 0)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.next_dir = (0, -1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.next_dir = (0, 1)

    def can_move(self, board, direction):
        next_x = self.x + direction[0] * self.speed
        next_y = self.y + direction[1] * self.speed
        future_rect = pygame.Rect(next_x, next_y, TILE_SIZE, TILE_SIZE)
        for wall in board.walls:
            if future_rect.colliderect(wall):
                return False
        return True


class Ghost(Entity):
    def __init__(self, x, y, color, scatter_target):
        super().__init__(x, y, color)
        self.start_pos = (x, y)
        self.scatter_target = scatter_target
        self.mode = 'scatter'
        self.frightened_timer = 0

    def reset(self):
        self.x, self.y = self.start_pos
        self.dir = (0, 0)
        self.mode = 'scatter'
        self.frightened_timer = 0

    def update(self, board, pacman, mode):
        if self.frightened_timer > 0:
            self.frightened_timer -= 1
            if self.at_center():
                self.dir = random.choice(self.valid_dirs(board))
            self.move()
            return
        else:
            self.mode = mode
        if self.at_center():
            if self.mode == 'scatter':
                target = self.scatter_target
            else:
                target = pacman.tile_pos()
            self.dir = self.next_step(board, target)
        self.move()

    def frighten(self):
        self.frightened_timer = FPS * 7
        self.dir = (-self.dir[0], -self.dir[1])

    def next_step(self, board, target):
        start = self.tile_pos()
        if start == target:
            return (0, 0)
        queue = deque([start])
        came_from = {start: None}
        while queue:
            current = queue.popleft()
            if current == target:
                break
            for n in self.neighbors(board, current):
                if n not in came_from:
                    queue.append(n)
                    came_from[n] = current
        current = target
        while came_from.get(current) and came_from[current] != start:
            current = came_from[current]
        if current in came_from:
            dx = current[0] - start[0]
            dy = current[1] - start[1]
            return (dx, dy)
        return random.choice(self.valid_dirs(board))

    def neighbors(self, board, tile):
        x, y = tile
        dirs = [(-1,0),(1,0),(0,-1),(0,1)]
        result = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not board.is_wall(nx, ny):
                result.append((nx, ny))
        return result

    def valid_dirs(self, board):
        x, y = self.tile_pos()
        dirs = [(-1,0),(1,0),(0,-1),(0,1)]
        valid = []
        for d in dirs:
            nx, ny = x + d[0], y + d[1]
            if not board.is_wall(nx, ny):
                valid.append(d)
        if valid:
            valid.remove((-self.dir[0], -self.dir[1])) if (-self.dir[0], -self.dir[1]) in valid and len(valid) > 1 else None
        return valid

    def at_center(self):
        return int(self.x) % TILE_SIZE == 0 and int(self.y) % TILE_SIZE == 0


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chaser")
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.pacman = Pacman(7 * TILE_SIZE, 9 * TILE_SIZE)
        self.ghosts = [
            Ghost(7 * TILE_SIZE, 6 * TILE_SIZE, RED, (14, 0)),
            Ghost(7 * TILE_SIZE, 6 * TILE_SIZE, PINK, (0, 0)),
            Ghost(7 * TILE_SIZE, 6 * TILE_SIZE, CYAN, (14, 11)),
            Ghost(7 * TILE_SIZE, 6 * TILE_SIZE, WHITE, (0, 11)),
        ]
        self.mode = 'scatter'
        self.mode_timer = FPS * 7

    def reset_positions(self):
        self.pacman.x = 7 * TILE_SIZE
        self.pacman.y = 9 * TILE_SIZE
        for g in self.ghosts:
            g.reset()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.pacman.handle_event(event)
            self.update_mode()
            power = self.pacman.update(self.board)
            if power:
                for g in self.ghosts:
                    g.frighten()
            for g in self.ghosts:
                g.update(self.board, self.pacman, self.mode)
            self.check_collisions()
            self.draw()
            if not self.board.dots and not self.board.power:
                running = False
        pygame.quit()

    def update_mode(self):
        self.mode_timer -= 1
        if self.mode_timer <= 0:
            if self.mode == 'scatter':
                self.mode = 'chase'
                self.mode_timer = FPS * 20
            else:
                self.mode = 'scatter'
                self.mode_timer = FPS * 7

    def check_collisions(self):
        p_rect = pygame.Rect(self.pacman.x, self.pacman.y, TILE_SIZE, TILE_SIZE)
        for g in self.ghosts:
            g_rect = pygame.Rect(g.x, g.y, TILE_SIZE, TILE_SIZE)
            if p_rect.colliderect(g_rect):
                if g.frightened_timer > 0:
                    g.reset()
                    self.pacman.score += 200
                else:
                    self.pacman.lives -= 1
                    if self.pacman.lives <= 0:
                        pygame.quit()
                        raise SystemExit
                    self.reset_positions()
                    break

    def draw(self):
        self.screen.fill(BLACK)
        self.board.draw(self.screen)
        self.pacman.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.draw_text(f"Score: {self.pacman.score}", 18, WHITE, 60, HEIGHT - 20)
        self.draw_text(f"Lives: {self.pacman.lives}", 18, WHITE, WIDTH - 80, HEIGHT - 20)
        pygame.display.flip()

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.SysFont('arial', size)
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(x, y))
        self.screen.blit(surface, rect)


if __name__ == '__main__':
    Game().run()
