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
human_food = Food(human.body)
human_score = 0

# RL Agent
env = SnakeEnv()
model = DQN.load("rl_agent/model")
obs = env.reset()
agent_score = 0

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

    # Human move and eat
    human.move()
    if human.get_head() == human_food.position:
        human.grow = True
        human_score += 1
        human_food = Food(human.body)

    # Human collision check
    if human.collides_with_self():
        winner = "AI Wins!" if agent_score >= human_score else "Human Wins!"
        draw_text(f"Game Over: {winner}", (180, 300))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

    # RL Agent logic
    action, _ = model.predict(obs)
    obs, reward, done, _ = env.step(action)

    if done:
        winner = "Human Wins!" if human_score > agent_score else "AI Wins!"
        draw_text(f"Game Over: {winner}", (180, 300))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()
    
    # Food drawing
    human_food.draw(screen)

    # Human snake drawing (head: bright green, tail: dark green)
    for i, segment in enumerate(human.body):
        color = (0, 200, 0) if i > 0 else (0, 255, 0)
        pygame.draw.rect(screen, color, pygame.Rect(segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # AI snake drawing (head: bright blue, tail: dark blue)
    for i, segment in enumerate(env.snake_body):
        color = (0, 0, 200) if i > 0 else (0, 0, 255)
        pygame.draw.rect(screen, color, pygame.Rect(segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Scoreboard
    draw_text(f"Human Score: {human_score}", (10, 10))
    draw_text(f"AI Score: {agent_score}", (400, 10))

    pygame.display.flip()
    clock.tick(10)
