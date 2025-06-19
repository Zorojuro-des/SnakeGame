# main.py
import pygame
import sys
from snake_game import Snake, Food, GRID_SIZE, CELL_SIZE, SCREEN_SIZE, UP, DOWN, LEFT, RIGHT
from stable_baselines3 import DQN
from rl_agent.env import SnakeEnv

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Snake Showdown")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Human player
human = Snake((0, 255, 0), (5, 5))

# RL Agent
env = SnakeEnv()
model = DQN.load("rl_agent/model")
obs = env.reset()
agent_positions = []

food = Food(human.body)
score = 0

def draw_text(text, pos):
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, pos)

while True:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Human control
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]: human.change_direction(UP)
    if keys[pygame.K_DOWN]: human.change_direction(DOWN)
    if keys[pygame.K_LEFT]: human.change_direction(LEFT)
    if keys[pygame.K_RIGHT]: human.change_direction(RIGHT)

    # Move both
    human.move()
    obs, _, _, _ = env.step(None)  # Run agent logic
    agent_positions = env.snake_body

    # Eat food
    if human.get_head() == food.position:
        human.grow = True
        score += 1
        food = Food(human.body)

    # Check game over
    if human.collides_with_self():
        draw_text("Game Over", (200, 300))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

    # Draw everything
    food.draw(screen)
    human.draw(screen)

    for pos in agent_positions:
        pygame.draw.rect(screen, (0, 0, 255),
                         pygame.Rect(pos[0]*CELL_SIZE, pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    draw_text(f"Score: {score}", (10, 10))
    pygame.display.flip()
    clock.tick(10)