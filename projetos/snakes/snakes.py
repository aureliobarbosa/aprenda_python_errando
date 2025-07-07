import pygame
import random

pygame.init()

# Configurações
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20
FPS = 10

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.SysFont('Arial', 25)

class SnakeGame:
    def __init__(self):
        self.snake = [[100, 50], [90, 50], [80, 50]]
        self.direction = 'RIGHT'
        self.food = self.generate_food()
        self.game_over = False

    def generate_food(self):
        x = random.randint(0, (SCREEN_WIDTH // BLOCK_SIZE) - 1) * BLOCK_SIZE
        y = random.randint(0, (SCREEN_HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE
        return [x, y]

    def move_snake(self):
        head = self.snake[0].copy()

        if self.direction == 'UP':
            head[1] -= BLOCK_SIZE
        elif self.direction == 'DOWN':
            head[1] += BLOCK_SIZE
        elif self.direction == 'LEFT':
            head[0] -= BLOCK_SIZE
        elif self.direction == 'RIGHT':
            head[0] += BLOCK_SIZE

        self.snake.insert(0, head)

        if head == self.food:
            self.food = self.generate_food()
        else:
            self.snake.pop()

        if (head[0] < 0 or head[0] >= SCREEN_WIDTH or
            head[1] < 0 or head[1] >= SCREEN_HEIGHT or
            head in self.snake[1:]):
            self.game_over = True

    def change_direction(self, direction):
        if direction == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        elif direction == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'
        elif direction == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        elif direction == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'

    def draw(self):
        screen.fill(BLACK)

        for segment in self.snake:
            pygame.draw.rect(screen, GREEN, (*segment, BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.rect(screen, RED, (*self.food, BLOCK_SIZE, BLOCK_SIZE))

        if self.game_over:
            game_over_text = font.render("Game Over! Press R to Restart.", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 3))

        pygame.display.flip()


def main():
    game = SnakeGame()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.change_direction('UP')
                elif event.key == pygame.K_DOWN:
                    game.change_direction('DOWN')
                elif event.key == pygame.K_LEFT:
                    game.change_direction('LEFT')
                elif event.key == pygame.K_RIGHT:
                    game.change_direction('RIGHT')
                elif event.key == pygame.K_r and game.game_over:
                    game.__init__()

        if not game.game_over:
            game.move_snake()

        game.draw()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
