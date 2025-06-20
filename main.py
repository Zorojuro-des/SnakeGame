import pygame
import sys
from snake_game import Snake, Food, GRID_SIZE, CELL_SIZE, SCREEN_SIZE, BORDER_SIZE, COLORS, draw_grid, draw_border, UP, DOWN, LEFT, RIGHT
from stable_baselines3 import DQN
from rl_agent.env import SnakeEnv

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE + 2 * BORDER_SIZE, SCREEN_SIZE + 2 * BORDER_SIZE))
pygame.display.set_caption("Snake Showdown: Human vs AI")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 24)

# Initialize human and food
human = Snake({'head': COLORS['human_head'], 'body': COLORS['human_body']}, (5, 5))
food = Food(human.body)
human_score = 0

# RL Agent
rl_env = SnakeEnv()
rl_model = DQN.load("rl_agent/model")
rl_obs = rl_env.reset()
ai = Snake({'head': COLORS['ai_head'], 'body': COLORS['ai_body']}, (15, 15))
agent_score = 0

def select_speed():
    selecting = True
    speed = 12  # Default
    while selecting:
        screen.fill(COLORS['bg_light'])
        draw_text("Select Snake Speed(press number(1,2 or 3) on the keyboard)", (SCREEN_SIZE // 2 - 120, SCREEN_SIZE // 2 - 60))
        draw_text("1. Slow (8 FPS)", (SCREEN_SIZE // 2 - 80, SCREEN_SIZE // 2 - 20))
        draw_text("2. Medium (12 FPS)", (SCREEN_SIZE // 2 - 80, SCREEN_SIZE // 2 + 10))
        draw_text("3. Fast (20 FPS)", (SCREEN_SIZE // 2 - 80, SCREEN_SIZE // 2 + 40))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    speed = 8
                    selecting = False
                elif event.key == pygame.K_2:
                    speed = 12
                    selecting = False
                elif event.key == pygame.K_3:
                    speed = 20
                    selecting = False
    return speed

def force_grow(self):
    self.snake_body.insert(0, self.snake_body[0])  # Duplicate head to grow

def draw_text(text, pos, color=COLORS['text']):
    shadow = font.render(text, True, COLORS['text_shadow'])
    screen.blit(shadow, (pos[0] + 2, pos[1] + 2))
    img = font.render(text, True, color)
    screen.blit(img, pos)

game_over = False
winner = ""
speed = select_speed()
while True:
    screen.fill(COLORS['bg_dark'])
    draw_grid(screen)
    draw_border(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and game_over and event.key == pygame.K_SPACE:
            # Reset game
            speed = select_speed()
            human = Snake({'head': COLORS['human_head'], 'body': COLORS['human_body']}, (5, 5))
            food = Food(human.body)
            human_score = 0

            rl_env = SnakeEnv()
            rl_obs = rl_env.reset()
            ai = Snake({'head': COLORS['ai_head'], 'body': COLORS['ai_body']}, (15, 15))
            agent_score = 0

            game_over = False
            winner = ""

    if not game_over:
        # Human movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: human.change_direction(UP)
        elif keys[pygame.K_DOWN]: human.change_direction(DOWN)
        elif keys[pygame.K_LEFT]: human.change_direction(LEFT)
        elif keys[pygame.K_RIGHT]: human.change_direction(RIGHT)

        human.move()
        if human.get_head() == food.position:
            human.grow = True
            human_score += 1
            food = Food(human.body)

        if human.collides_with_self():
            game_over = True
            winner = "🤖 AI Wins!"

        # RL Agent move
        action, _ = rl_model.predict(rl_obs)
        rl_obs, _, rl_done, _ = rl_env.step(action)

        ai.body = rl_env.snake_body.copy()
        ai.direction = rl_env.direction

        if ai.get_head() == food.position:
            rl_env.force_grow()
            agent_score += 1
            food = Food(human.body + ai.body)


        # Check collision between AI and Human
        if human.get_head() in ai.body:
            game_over = True
            winner = "🤖 AI Wins!"
        elif ai.get_head() in human.body:
            game_over = True
            winner = "🎮 Human Wins!"

        if rl_done:
            game_over = True
            winner = "🎮 Human Wins!"

    # Draw everything
    food.draw(screen)
    human.draw(screen)
    ai.draw(screen)

    draw_text(f"Human: {human_score}", (BORDER_SIZE, 10))
    draw_text(f"AI: {agent_score}", (SCREEN_SIZE - 100, 10))

    if game_over:
        draw_text("Game Over!", (SCREEN_SIZE // 2 - 80, SCREEN_SIZE // 2 - 20))
        draw_text(f"{winner}", (SCREEN_SIZE // 2 - 100, SCREEN_SIZE // 2 + 10))
        draw_text("Press SPACE to restart", (SCREEN_SIZE // 2 - 130, SCREEN_SIZE // 2 + 40))

    pygame.display.flip()
    clock.tick(speed)
