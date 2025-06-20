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

# RL Agent setup
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

    # Move human
    human.move()

    # Human eats food
    if human.get_head() == human_food.position:
        human.grow = True
        human_score += 1
        human_food = Food(human.body)

    # Check human death
    if human.collides_with_self():
        draw_text("Game Over (Human)", (180, 280))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

    # AI Agent
    action, _ = model.predict(obs)
    obs, reward, done, _ = env.step(action)

    if done:
        draw_text("AI Crashed", (200, 320))
        pygame.display.flip()
        pygame.time.wait(1000)
        obs = env.reset()
        agent_score = 0

    # Draw everything
    human_food.draw(screen)
    human.draw(screen)

    for pos in env.snake_body:
        pygame.draw.rect(screen, (0, 0, 255),
                         pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Scores
    draw_text(f"Human Score: {human_score}", (10, 10))
    draw_text(f"AI Score: {agent_score}", (400, 10))

    pygame.display.flip()
    clock.tick(10)
