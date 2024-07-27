import pygame
import random
import sys
from queue import PriorityQueue
from datetime import datetime

WIDTH, HEIGHT = 800, 800
GRID_SIZE = 20
CELL_SIZE = WIDTH // GRID_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BG_COLOR = (50, 50, 50)

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Dungeon Crawler")

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frozen = False

    def move_towards(self, target_x, target_y, grid):
        if not self.frozen:
            path = a_star_search((self.x, self.y), (target_x, target_y), grid)
            if path and len(path) > 1:
                self.x, self.y = path[1]

class Treasure:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(start, goal, grid):
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {node: float('inf') for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float('inf') for row in grid for node in row}
    f_score[start] = heuristic(start, goal)

    open_set_hash = {start}

    while not open_set.empty():
        current = open_set.get()[1]
        open_set_hash.remove(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for neighbor in get_neighbors(current, grid):
            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                if neighbor not in open_set_hash:
                    open_set_hash.add(neighbor)
                    open_set.put((f_score[neighbor], neighbor))

    return None

def get_neighbors(pos, grid):
    neighbors = []
    x, y = pos
    if x > 0:
        neighbors.append((x - 1, y))
    if x < GRID_SIZE - 1:
        neighbors.append((x + 1, y))
    if y > 0:
        neighbors.append((x, y - 1))
    if y < GRID_SIZE - 1:
        neighbors.append((x, y + 1))
    return neighbors

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(win, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(win, BLACK, (0, y), (WIDTH, y))

def draw(win, player, enemies, treasures, power_ups, message=None, stats=None):
    win.fill(BG_COLOR)
    draw_grid()

    pygame.draw.circle(win, RED, (player.x * CELL_SIZE + CELL_SIZE // 2, player.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)

    for enemy in enemies:
        pygame.draw.rect(win, BLUE, (enemy.x * CELL_SIZE, enemy.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for treasure in treasures:
        pygame.draw.polygon(win, YELLOW, [
            (treasure.x * CELL_SIZE + CELL_SIZE // 2, treasure.y * CELL_SIZE),
            (treasure.x * CELL_SIZE, treasure.y * CELL_SIZE + CELL_SIZE),
            (treasure.x * CELL_SIZE + CELL_SIZE, treasure.y * CELL_SIZE + CELL_SIZE)
        ])

    for power_up in power_ups:
        pygame.draw.circle(win, PURPLE, (power_up.x * CELL_SIZE + CELL_SIZE // 2, power_up.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)

    if message:
        font = pygame.font.SysFont(None, 48)
        text = font.render(message, True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        win.blit(text, text_rect)

    if stats:
        font = pygame.font.SysFont(None, 36)
        stats_text = f"Treasures Collected: {stats['treasures']}    Time: {stats['time']:.2f}s"
        text = font.render(stats_text, True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        win.blit(text, text_rect)

    pygame.display.update()

def draw_intro(win):
    win.fill(BG_COLOR)
    font = pygame.font.SysFont(None, 36)

    instructions = [
        "Welcome to AI Dungeon Crawler!",
        "",
        "Instructions:",
        "Red Circle: You (Player)",
        "Blue Square: Enemies (Avoid them)",
        "Yellow Triangle: Treasures (Collect them)",
        "Purple Circle: Power-ups (Freeze enemies)",
        "",
        "Use arrow keys to move.",
        "Collect all treasures to win.",
        "Avoid enemies or you'll lose.",
        "Collect power-ups to freeze enemies.",
        "",
        "Press any key to start the game."
    ]

    y_offset = 100
    for line in instructions:
        text = font.render(line, True, WHITE)
        win.blit(text, (50, y_offset))
        y_offset += 40

    pygame.display.update()

def restart_game():
    global player, enemies, treasures, power_ups, enemy_move_counter, power_up_timer, game_over, show_intro, start_time, collected_treasures
    player = Player(0, 0)
    enemies = [Enemy(random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)) for _ in range(5)]
    treasures = [Treasure(random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)) for _ in range(5)]
    power_ups = [PowerUp(random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)) for _ in range(3)]
    enemy_move_counter = 0
    power_up_timer = 0
    game_over = False
    show_intro = True
    start_time = datetime.now()
    collected_treasures = 0

def main():
    global player, enemies, treasures, power_ups, enemy_move_counter, power_up_timer, game_over, show_intro, start_time, collected_treasures
    clock = pygame.time.Clock()

    grid = [[(i, j) for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]

    restart_game()

    enemy_move_threshold = 3  
    power_up_duration = 100  

    run = True
    while run:
        if show_intro:
            draw_intro(win)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    show_intro = False
        else:
            clock.tick(10)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN and not game_over:
                    if event.key == pygame.K_UP and player.y > 0:
                        player.move(0, -1)
                    elif event.key == pygame.K_DOWN and player.y < GRID_SIZE - 1:
                        player.move(0, 1)
                    elif event.key == pygame.K_LEFT and player.x > 0:
                        player.move(-1, 0)
                    elif event.key == pygame.K_RIGHT and player.x < GRID_SIZE - 1:
                        player.move(1, 0)
                elif event.type == pygame.KEYDOWN and game_over:
                    if event.key == pygame.K_r:
                        restart_game()
                    elif event.key == pygame.K_q:
                        run = False

            if power_up_timer > 0:
                power_up_timer -= 1
                if power_up_timer == 0:
                    for enemy in enemies:
                        enemy.frozen = False

            if not game_over:
                enemy_move_counter += 1
                if enemy_move_counter >= enemy_move_threshold:
                    for enemy in enemies:
                        enemy.move_towards(player.x, player.y, grid)
                    enemy_move_counter = 0

                for enemy in enemies:
                    if player.x == enemy.x and player.y == enemy.y:
                        if enemy.frozen:
                            continue
                        game_over = True
                        end_time = datetime.now()
                        game_duration = (end_time - start_time).total_seconds()

                for treasure in treasures[:]:
                    if player.x == treasure.x and player.y == treasure.y:
                        treasures.remove(treasure)
                        collected_treasures += 1

                for power_up in power_ups[:]:
                    if player.x == power_up.x and player.y == power_up.y:
                        power_ups.remove(power_up)
                        power_up_timer = power_up_duration
                        for enemy in enemies:
                            enemy.frozen = True

            if game_over:
                stats = {'treasures': collected_treasures, 'time': game_duration}
                draw(win, player, enemies, treasures, power_ups, message="Game Over! Press R to Restart or Q to Quit", stats=stats)
            elif not treasures:
                game_over = True
                end_time = datetime.now()
                game_duration = (end_time - start_time).total_seconds()
                stats = {'treasures': collected_treasures, 'time': game_duration}
                draw(win, player, enemies, treasures, power_ups, message="You Win! Press R to Restart or Q to Quit", stats=stats)
            else:
                draw(win, player, enemies, treasures, power_ups)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
