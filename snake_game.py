import pygame
import random
import math

CELL_SIZE = 20
GRID_SIZE = 30
SCREEN_SIZE = CELL_SIZE * GRID_SIZE
BORDER_SIZE = 50

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Enhanced color palette
COLORS = {
    'bg_dark': (15, 15, 25),
    'bg_light': (25, 25, 40),
    'grid': (40, 40, 60),
    'human_head': (50, 255, 100),
    'human_body': (30, 200, 80),
    'ai_head': (100, 150, 255),
    'ai_body': (60, 100, 200),
    'food': (255, 80, 80),
    'food_glow': (255, 120, 120),
    'text': (255, 255, 255),
    'text_shadow': (50, 50, 50),
    'border': (80, 80, 120)
}

def draw_rounded_rect(surface, color, rect, radius):
    """Draw a rounded rectangle"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_gradient_rect(surface, color1, color2, rect):
    """Draw a rectangle with vertical gradient"""
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), 
                        (rect.x, rect.y + y), 
                        (rect.x + rect.width, rect.y + y))

def draw_glow_circle(surface, color, center, radius, glow_radius):
    """Draw a glowing circle effect"""
    for i in range(glow_radius):
        alpha = 255 - (i * 255 // glow_radius)
        glow_color = (*color, alpha)
        glow_surface = pygame.Surface((radius * 2 + i * 2, radius * 2 + i * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, 
                          (radius + i, radius + i), radius + i)
        surface.blit(glow_surface, (center[0] - radius - i, center[1] - radius - i), 
                    special_flags=pygame.BLEND_ALPHA_SDL2)

class Snake:
    def __init__(self, color_scheme, init_pos):
        self.body = [init_pos]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color_scheme = color_scheme
        self.grow = False
        self.pulse_timer = 0

    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_SIZE, (head_y + dy) % GRID_SIZE)
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, new_direction):
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def collides_with_self(self):
        return self.body[0] in self.body[1:]

    def get_head(self):
        return self.body[0]

    def draw(self, screen):
        self.pulse_timer += 0.1
        
        for i, segment in enumerate(self.body):
            x = segment[0] * CELL_SIZE + BORDER_SIZE
            y = segment[1] * CELL_SIZE + BORDER_SIZE
            
            if i == 0:  # Head
                # Pulsing effect for head
                pulse = math.sin(self.pulse_timer) * 2 + 2
                head_size = CELL_SIZE - 2 + pulse
                head_rect = pygame.Rect(x + (CELL_SIZE - head_size) // 2, 
                                      y + (CELL_SIZE - head_size) // 2, 
                                      head_size, head_size)
                
                # Draw head with gradient
                draw_gradient_rect(screen, self.color_scheme['head'], 
                                 self.color_scheme['body'], head_rect)
                draw_rounded_rect(screen, self.color_scheme['head'], head_rect, 8)
                
                # Add eyes
                eye_size = 3
                eye1_pos = (x + 6, y + 6)
                eye2_pos = (x + CELL_SIZE - 9, y + 6)
                pygame.draw.circle(screen, (255, 255, 255), eye1_pos, eye_size)
                pygame.draw.circle(screen, (255, 255, 255), eye2_pos, eye_size)
                pygame.draw.circle(screen, (0, 0, 0), eye1_pos, eye_size - 1)
                pygame.draw.circle(screen, (0, 0, 0), eye2_pos, eye_size - 1)
                
            else:  # Body
                body_rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                # Gradient effect for body segments
                alpha = max(100, 255 - i * 10)
                body_color = (*self.color_scheme['body'], min(255, alpha))
                
                body_surface = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4), pygame.SRCALPHA)
                draw_rounded_rect(body_surface, body_color, 
                                pygame.Rect(0, 0, CELL_SIZE - 4, CELL_SIZE - 4), 6)
                screen.blit(body_surface, (x + 2, y + 2))

class Food:
    def __init__(self, snake_positions):
        self.position = self.spawn(snake_positions)
        self.pulse_timer = 0
        # self.sparkles = []
        # self.generate_sparkles()

    def spawn(self, occupied):
        while True:
            pos = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            if pos not in occupied:
                return pos

    # def generate_sparkles(self):
    #     """Generate sparkle effects around food"""
    #     self.sparkles = []
    #     for _ in range(6):
    #         angle = random.uniform(0, 2 * math.pi)
    #         distance = random.uniform(15, 25)
    #         self.sparkles.append({
    #             'angle': angle,
    #             'distance': distance,
    #             'size': random.uniform(1, 3),
    #             'alpha': random.randint(100, 255)
    #         })

    def draw(self, screen):
        self.pulse_timer += 0.15
        
        x = self.position[0] * CELL_SIZE + BORDER_SIZE + CELL_SIZE // 2
        y = self.position[1] * CELL_SIZE + BORDER_SIZE + CELL_SIZE // 2
        
        # Pulsing food with glow effect
        pulse = math.sin(self.pulse_timer) * 3 + 3
        food_radius = CELL_SIZE // 2 - 2 + pulse
        
        # Draw glow effect
        glow_surface = pygame.Surface((food_radius * 4, food_radius * 4), pygame.SRCALPHA)
        for i in range(10):
            alpha = 50 - i * 5
            if alpha > 0:
                pygame.draw.circle(glow_surface, (*COLORS['food_glow'], alpha),
                                 (food_radius * 2, food_radius * 2), 
                                 food_radius + i * 2)
        screen.blit(glow_surface, (x - food_radius * 2, y - food_radius * 2))
        
        # Draw main food
        pygame.draw.circle(screen, COLORS['food'], (x, y), int(food_radius))
        pygame.draw.circle(screen, (255, 150, 150), (x, y), int(food_radius * 0.7))
        pygame.draw.circle(screen, (255, 200, 200), (x, y), int(food_radius * 0.4))
        
        # Draw sparkles
        # for sparkle in self.sparkles:
        #     sparkle_x = x + math.cos(sparkle['angle'] + self.pulse_timer) * sparkle['distance']
        #     sparkle_y = y + math.sin(sparkle['angle'] + self.pulse_timer) * sparkle['distance']
            
        #     sparkle_surface = pygame.Surface((sparkle['size'] * 2, sparkle['size'] * 2), pygame.SRCALPHA)
        #     pygame.draw.circle(sparkle_surface, (255, 255, 255, sparkle['alpha']),
        #                      (sparkle['size'], sparkle['size']), sparkle['size'])
        #     screen.blit(sparkle_surface, (sparkle_x - sparkle['size'], sparkle_y - sparkle['size']))

def draw_grid(screen):
    """Draw a subtle grid pattern"""
    for x in range(0, GRID_SIZE + 1):
        pygame.draw.line(screen, COLORS['grid'], 
                        (BORDER_SIZE + x * CELL_SIZE, BORDER_SIZE),
                        (BORDER_SIZE + x * CELL_SIZE, BORDER_SIZE + SCREEN_SIZE), 1)
    for y in range(0, GRID_SIZE + 1):
        pygame.draw.line(screen, COLORS['grid'],
                        (BORDER_SIZE, BORDER_SIZE + y * CELL_SIZE),
                        (BORDER_SIZE + SCREEN_SIZE, BORDER_SIZE + y * CELL_SIZE), 1)

def draw_border(screen):
    """Draw decorative border"""
    border_rect = pygame.Rect(BORDER_SIZE - 5, BORDER_SIZE - 5, 
                             SCREEN_SIZE + 10, SCREEN_SIZE + 10)
    pygame.draw.rect(screen, COLORS['border'], border_rect, 5)
    
    # Inner border glow
    inner_border = pygame.Rect(BORDER_SIZE - 2, BORDER_SIZE - 2,
                              SCREEN_SIZE + 4, SCREEN_SIZE + 4)
    pygame.draw.rect(screen, (120, 120, 180), inner_border, 2)
