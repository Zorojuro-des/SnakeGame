import numpy as np
import pygame
from enum import Enum
from collections import deque
import random
import math

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class SnakeGame:
    def __init__(self, width=36, height=36, gui=False):
        self.width = width
        self.height = height
        self.gui = gui
        self.reset()
        
        if gui:
            pygame.init()
            self.cell_size = 20
            self.screen_width = width * self.cell_size
            self.screen_height = height * self.cell_size + 80
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("🐍 RETRO SNAKE BATTLE 🐍")
            
            # Enhanced fonts with retro styling
            self.font_small = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_large = pygame.font.Font(None, 48)
            self.font_title = pygame.font.Font(None, 64)
            
            # Retro color palette
            self.colors = {
                'background': (15, 15, 25),           # Dark navy
                'grid': (25, 35, 45),                 # Subtle grid
                'snake1_head': (0, 255, 150),         # Bright green
                'snake1_body': (0, 200, 120),         # Darker green
                'snake1_tail': (0, 150, 90),          # Even darker green
                'snake2_head': (255, 100, 255),       # Bright magenta
                'snake2_body': (200, 80, 200),        # Darker magenta
                'snake2_tail': (150, 60, 150),        # Even darker magenta
                'food': (255, 255, 100),              # Bright yellow
                'food_glow': (255, 255, 200),         # Yellow glow
                'text_primary': (255, 255, 255),      # White
                'text_secondary': (180, 180, 180),    # Light gray
                'ui_bg': (20, 25, 35),                # UI background
                'ui_border': (60, 80, 100),           # UI border
                'glow_green': (0, 255, 150, 50),      # Transparent green glow
                'glow_magenta': (255, 100, 255, 50),  # Transparent magenta glow
                'scanline': (255, 255, 255, 8),       # Subtle scanlines
            }
            
            # Animation variables
            self.food_pulse = 0
            self.scanline_offset = 0
            self.game_time = 0
    
    def reset(self):
        self.snake1 = deque([(self.width//4, self.height//2)])
        self.snake2 = deque([(3*self.width//4, self.height//2)])
        self.direction1 = Direction.RIGHT
        self.direction2 = Direction.LEFT
        self.food = self._place_food()
        self.score1 = 0
        self.score2 = 0
        self.done = False
        self.winner = None
        self.steps = 0
        self.last_food_distance2 = self._food_distance(2)
        return self._get_state()
    
    def _place_food(self):
        while True:
            food = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if food not in self.snake1 and food not in self.snake2:
                return food
    
    def _food_distance(self, snake_num):
        if snake_num == 1:
            head = self.snake1[0]
        else:
            head = self.snake2[0]
        return abs(head[0] - self.food[0]) + abs(head[1] - self.food[1])
    
    def _get_state(self):
        # Create a grid representation
        grid = np.zeros((self.height, self.width, 3), dtype=np.float32)
        
        # Mark snake1 positions (channel 0)
        for segment in self.snake1:
            grid[segment[1], segment[0], 0] = 1.0
        
        # Mark snake2 positions (channel 1)
        for segment in self.snake2:
            grid[segment[1], segment[0], 1] = 1.0
        
        # Mark food position (channel 2)
        grid[self.food[1], self.food[0], 2] = 1.0
        
        # Add direction information
        direction1_onehot = np.zeros(4, dtype=np.float32)
        direction1_onehot[self.direction1.value] = 1.0
        
        direction2_onehot = np.zeros(4, dtype=np.float32)
        direction2_onehot[self.direction2.value] = 1.0
        
        # Add food direction information (relative to snake2 head)
        head_x, head_y = self.snake2[0]
        food_dx = self.food[0] - head_x
        food_dy = self.food[1] - head_y
        food_direction = np.array([food_dx, food_dy], dtype=np.float32)
        
        # Normalize food direction
        if abs(food_dx) + abs(food_dy) > 0:
            food_direction = food_direction / (abs(food_dx) + abs(food_dy))
        
        # Flatten everything
        flat_grid = grid.flatten()
        state = np.concatenate([flat_grid, direction1_onehot, direction2_onehot, food_direction])
        
        return state
    
    def step(self, action1=None, action2=None):
        if self.done:
            return self._get_state(), (0, 0), self.done, self.winner
        
        self.steps += 1
        
        # Update directions
        if action1 is not None:
            self._update_direction(1, action1)
        if action2 is not None:
            self._update_direction(2, action2)
        
        # Move snakes
        reward1, dead1 = self._move_snake(1)
        reward2, dead2 = self._move_snake(2)
        
        # Additional reward for moving toward food (for AI snake)
        current_food_distance = self._food_distance(2)
        if current_food_distance < self.last_food_distance2:
            reward2 += 1
        elif current_food_distance > self.last_food_distance2:
            reward2 -= 0.5
        self.last_food_distance2 = current_food_distance
        
        # Check for collisions between snakes
        head1 = self.snake1[0]
        head2 = self.snake2[0]
        
        if head1 == head2:
            self.done = True
            self.winner = "Draw"
            return self._get_state(), (reward1-10, reward2-10), self.done, self.winner
        
        if head1 in list(self.snake2)[1:]:
            self.done = True
            self.winner = "Snake2"
            return self._get_state(), (reward1-10, reward2+5), self.done, self.winner
        
        if head2 in list(self.snake1)[1:]:
            self.done = True
            self.winner = "Snake1"
            return self._get_state(), (reward1+5, reward2-10), self.done, self.winner
        
        # Check for starvation
        if self.steps > 100 * (self.score1 + self.score2 + 1):
            self.done = True
            if self.score1 > self.score2:
                self.winner = "Snake1"
            elif self.score2 > self.score1:
                self.winner = "Snake2"
            else:
                self.winner = "Draw"
            return self._get_state(), (reward1, reward2), self.done, self.winner
        
        return self._get_state(), (reward1, reward2), self.done, None
    
    def _update_direction(self, snake_num, action):
        if snake_num == 1:
            current_dir = self.direction1
            new_dir = Direction(action)
            if (current_dir == Direction.UP and new_dir != Direction.DOWN) or \
               (current_dir == Direction.DOWN and new_dir != Direction.UP) or \
               (current_dir == Direction.LEFT and new_dir != Direction.RIGHT) or \
               (current_dir == Direction.RIGHT and new_dir != Direction.LEFT):
                self.direction1 = new_dir
        else:
            current_dir = self.direction2
            new_dir = Direction(action)
            if (current_dir == Direction.UP and new_dir != Direction.DOWN) or \
               (current_dir == Direction.DOWN and new_dir != Direction.UP) or \
               (current_dir == Direction.LEFT and new_dir != Direction.RIGHT) or \
               (current_dir == Direction.RIGHT and new_dir != Direction.LEFT):
                self.direction2 = new_dir
    
    def _move_snake(self, snake_num):
        if snake_num == 1:
            snake = self.snake1
            direction = self.direction1
            food = self.food
        else:
            snake = self.snake2
            direction = self.direction2
            food = self.food
        
        # Calculate new head position
        head_x, head_y = snake[0]
        if direction == Direction.UP:
            new_head = (head_x, (head_y - 1) % self.height)
        elif direction == Direction.DOWN:
            new_head = (head_x, (head_y + 1) % self.height)
        elif direction == Direction.LEFT:
            new_head = ((head_x - 1) % self.width, head_y)
        else:  # RIGHT
            new_head = ((head_x + 1) % self.width, head_y)
        
        # Check for self-collision
        if new_head in list(snake)[:-1]:
            self.done = True
            # Set winner based on which snake collided with itself
            if snake_num == 1:
                self.winner = "Snake2"  # AI wins if human crashes
            else:
                self.winner = "Snake1"  # Human wins if AI crashes
            return -10, True
        
        # Move snake
        snake.appendleft(new_head)
        
        # Check if food eaten
        if new_head == food:
            self.food = self._place_food()
            if snake_num == 1:
                self.score1 += 1
            else:
                self.score2 += 1
            return 10, False
        else:
            snake.pop()
            return 0, False
    
    def _draw_glow_effect(self, surface, color, center, radius):
        """Draw a glowing effect around a point"""
        glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        for i in range(radius, 0, -2):
            alpha = max(5, 30 - i)
            glow_color = (*color[:3], alpha)
            pygame.draw.circle(glow_surface, glow_color, (radius * 2, radius * 2), i)
        surface.blit(glow_surface, (center[0] - radius * 2, center[1] - radius * 2))
    
    def _draw_snake_segment(self, x, y, snake_num, segment_index, total_segments):
        """Draw an enhanced snake segment with gradient and glow"""
        rect = pygame.Rect(x * self.cell_size, y * self.cell_size + 80, 
                          self.cell_size, self.cell_size)
        
        # Calculate color based on position in snake (gradient effect)
        if snake_num == 1:
            if segment_index == 0:  # Head
                color = self.colors['snake1_head']
                glow_color = self.colors['glow_green']
            elif segment_index < total_segments * 0.3:  # Body
                color = self.colors['snake1_body']
                glow_color = None
            else:  # Tail
                color = self.colors['snake1_tail']
                glow_color = None
        else:
            if segment_index == 0:  # Head
                color = self.colors['snake2_head']
                glow_color = self.colors['glow_magenta']
            elif segment_index < total_segments * 0.3:  # Body
                color = self.colors['snake2_body']
                glow_color = None
            else:  # Tail
                color = self.colors['snake2_tail']
                glow_color = None
        
        # Draw glow effect for head
        if glow_color and segment_index == 0:
            center = (rect.centerx, rect.centery)
            self._draw_glow_effect(self.screen, glow_color, center, self.cell_size)
        
        # Draw main segment with rounded corners
        pygame.draw.rect(self.screen, color, rect, border_radius=3)
        
        # Add highlight for 3D effect
        highlight_rect = pygame.Rect(rect.x + 2, rect.y + 2, 
                                   rect.width - 4, rect.height - 4)
        highlight_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.rect(self.screen, highlight_color, highlight_rect, 
                        width=1, border_radius=2)
    
    def _draw_food(self):
        """Draw animated food with pulsing glow effect"""
        food_x, food_y = self.food
        rect = pygame.Rect(food_x * self.cell_size, food_y * self.cell_size + 80,
                          self.cell_size, self.cell_size)
        
        # Pulsing animation
        pulse_size = int(3 * math.sin(self.food_pulse * 0.3))
        expanded_rect = rect.inflate(pulse_size, pulse_size)
        
        # Draw glow effect
        center = (rect.centerx, rect.centery)
        glow_radius = self.cell_size + pulse_size
        self._draw_glow_effect(self.screen, self.colors['food_glow'], center, glow_radius)
        
        # Draw main food
        pygame.draw.ellipse(self.screen, self.colors['food'], expanded_rect)
        
        # Add sparkle effect
        sparkle_color = (255, 255, 255)
        sparkle_points = [
            (rect.centerx - 3, rect.centery - 3),
            (rect.centerx + 3, rect.centery + 3),
            (rect.centerx + 3, rect.centery - 3),
            (rect.centerx - 3, rect.centery + 3)
        ]
        for point in sparkle_points:
            pygame.draw.circle(self.screen, sparkle_color, point, 1)
    
    def _draw_scanlines(self):
        """Draw retro CRT scanlines effect"""
        scanline_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for y in range(0, self.screen_height, 4):
            pygame.draw.line(scanline_surface, self.colors['scanline'], 
                           (0, y + self.scanline_offset), (self.screen_width, y + self.scanline_offset))
        self.screen.blit(scanline_surface, (0, 0))
    
    def _draw_ui_panel(self):
        """Draw enhanced UI panel with retro styling"""
        # Main UI background
        ui_rect = pygame.Rect(0, 0, self.screen_width, 80)
        pygame.draw.rect(self.screen, self.colors['ui_bg'], ui_rect)
        
        # Border lines
        pygame.draw.line(self.screen, self.colors['ui_border'], 
                        (0, 78), (self.screen_width, 78), 2)
        pygame.draw.line(self.screen, self.colors['ui_border'], 
                        (0, 80), (self.screen_width, 80), 1)
        
        # Title
        title_text = self.font_medium.render("RETRO SNAKE BATTLE", True, self.colors['text_primary'])
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 25))
        self.screen.blit(title_text, title_rect)
        
        # Player scores with icons
        human_text = self.font_small.render(f"🎮 HUMAN: {self.score1:02d}", True, self.colors['snake1_head'])
        ai_text = self.font_small.render(f"🤖 AI: {self.score2:02d}", True, self.colors['snake2_head'])
        
        self.screen.blit(human_text, (20, 50))
        self.screen.blit(ai_text, (self.screen_width - 120, 50))
        
        # Game stats
        steps_text = self.font_small.render(f"MOVES: {self.steps}", True, self.colors['text_secondary'])
        steps_rect = steps_text.get_rect(center=(self.screen_width // 2, 55))
        self.screen.blit(steps_text, steps_rect)
    
    def _draw_game_over_screen(self):
        """Draw enhanced game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Glitch effect for game over text
        center_y = self.screen_height // 2
        
        # Winner announcement
        if self.winner == "Snake1":
            winner_text = "🎮 HUMAN WINS! 🎮"
            winner_color = self.colors['snake1_head']
        elif self.winner == "Snake2":
            winner_text = "🤖 AI WINS! 🤖"
            winner_color = self.colors['snake2_head']
        else:
            winner_text = "⚡ DRAW! ⚡"
            winner_color = self.colors['text_primary']
        
        # Main winner text with glow
        winner_surface = self.font_large.render(winner_text, True, winner_color)
        winner_rect = winner_surface.get_rect(center=(self.screen_width // 2, center_y - 40))
        
        # Draw glow behind text
        glow_surface = self.font_large.render(winner_text, True, (*winner_color[:3], 100))
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_rect = winner_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(winner_surface, winner_rect)
        
        # Final scores
        score_text = f"FINAL SCORE - HUMAN: {self.score1}  AI: {self.score2}"
        score_surface = self.font_medium.render(score_text, True, self.colors['text_secondary'])
        score_rect = score_surface.get_rect(center=(self.screen_width // 2, center_y + 20))
        self.screen.blit(score_surface, score_rect)
        
        # Restart instruction with blinking effect
        blink = int(self.game_time * 3) % 2
        if blink:
            restart_text = "PRESS [R] TO RESTART"
            restart_surface = self.font_small.render(restart_text, True, self.colors['text_primary'])
            restart_rect = restart_surface.get_rect(center=(self.screen_width // 2, center_y + 60))
            self.screen.blit(restart_surface, restart_rect)
    
    def render(self):
        if not self.gui:
            return
        
        # Update animation variables
        self.food_pulse += 1
        self.scanline_offset = (self.scanline_offset + 1) % 4
        self.game_time += 0.016  # Approximate 60 FPS
        
        # Clear screen with background
        self.screen.fill(self.colors['background'])
        
        # Draw subtle grid
        for x in range(0, self.screen_width, self.cell_size):
            pygame.draw.line(self.screen, self.colors['grid'], 
                           (x, 80), (x, self.screen_height), 1)
        for y in range(80, self.screen_height, self.cell_size):
            pygame.draw.line(self.screen, self.colors['grid'], 
                           (0, y), (self.screen_width, y), 1)
        
        # Draw UI panel
        self._draw_ui_panel()
        
        # Draw food with animation
        self._draw_food()
        
        # Draw snakes with enhanced visuals
        for i, segment in enumerate(self.snake1):
            x, y = segment
            self._draw_snake_segment(x, y, 1, i, len(self.snake1))
        
        for i, segment in enumerate(self.snake2):
            x, y = segment
            self._draw_snake_segment(x, y, 2, i, len(self.snake2))
        
        # Draw game over screen
        if self.done and self.winner:
            self._draw_game_over_screen()
        
        # Add retro scanlines effect
        self._draw_scanlines()
        
        pygame.display.flip()
    
    def close(self):
        if self.gui:
            pygame.quit()
