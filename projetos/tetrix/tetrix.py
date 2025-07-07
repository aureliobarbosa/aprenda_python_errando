import pygame
import random

pygame.init()

# Constantes
CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = 400
HEIGHT = ROWS * CELL_SIZE
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris Completo")
CLOCK = pygame.time.Clock()

# Cores
COLORS = [
    (255, 0, 0),    # vermelho
    (0, 255, 0),    # verde
    (0, 0, 255),    # azul
    (255, 255, 0),  # amarelo
    (255, 0, 255),  # magenta
    (0, 255, 255),  # ciano
    (255, 165, 0)   # laranja
]
BACKGROUND = (30, 30, 30)

# Peças
SHAPES = [
    [[1, 1, 1, 1]],              # I
    [[1, 1], [1, 1]],            # O
    [[0, 1, 0], [1, 1, 1]],      # T
    [[1, 1, 0], [0, 1, 1]],      # S
    [[0, 1, 1], [1, 1, 0]],      # Z
    [[1, 0, 0], [1, 1, 1]],      # L
    [[0, 0, 1], [1, 1, 1]]       # J
]

def new_piece():
    shape = random.choice(SHAPES)
    color = random.choice(COLORS)
    return {
        "shape": shape,
        "color": color,
        "x": COLS // 2 - len(shape[0]) // 2,
        "y": 0
    }

def check_collision(piece, dx, dy):
    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                nx = piece["x"] + x + dx
                ny = piece["y"] + y + dy
                
                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return True
                if ny >= 0 and grid[ny][nx]:
                    return True
    return False

def lock_piece(piece):
    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell and piece["y"] + y >= 0:
                grid[piece["y"] + y][piece["x"] + x] = piece["color"]

def clear_lines():
    global score
    lines_to_clear = [i for i, row in enumerate(grid) if all(row)]
    for i in lines_to_clear:
        del grid[i]
        grid.insert(0, [0 for _ in range(COLS)])
    score += len(lines_to_clear) * 100

def draw_grid():
    SCREEN.fill(BACKGROUND)
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x]
            if color:
                pygame.draw.rect(SCREEN, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                px = (piece["x"] + x) * CELL_SIZE
                py = (piece["y"] + y) * CELL_SIZE
                pygame.draw.rect(SCREEN, piece["color"], (px, py, CELL_SIZE, CELL_SIZE))

    font = pygame.font.SysFont(None, 28)
    text = font.render(f"Pontos: {score}", True, (255, 255, 255))
    SCREEN.blit(text, (10, 10))
    pygame.display.update()

def show_game_over():
    font = pygame.font.SysFont("arial", 40)
    SCREEN.fill((0, 0, 0))
    over_text = font.render("GAME OVER", True, (255, 0, 0))
    score_text = font.render(f"Pontos: {score}", True, (255, 255, 255))
    continue_text = font.render("Pressione Enter para sair", True, (200, 200, 200))

    SCREEN.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 60))
    SCREEN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    SCREEN.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 60))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    waiting = False

# Inicialização
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
piece = new_piece()
fall_timer = 0
fall_speed = 500
score = 0

running = True
while running:
    dt = CLOCK.tick(60)
    fall_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        if not check_collision(piece, -1, 0):
            piece["x"] -= 1
            pygame.time.delay(100)

    if keys[pygame.K_RIGHT]:
        if not check_collision(piece, 1, 0):
            piece["x"] += 1
            pygame.time.delay(100)

    if keys[pygame.K_DOWN]:
        if not check_collision(piece, 0, 1):
            piece["y"] += 1
            fall_timer = 0

    if fall_timer >= fall_speed:
        if not check_collision(piece, 0, 1):
            piece["y"] += 1
        else:
            if piece["y"] < 0:
                show_game_over()
                running = False
                break
            lock_piece(piece)
            clear_lines()
            piece = new_piece()
        fall_timer = 0

    draw_grid()

pygame.quit()