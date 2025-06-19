# snake_game.py
import pygame
import random

CELL_SIZE = 20
GRID_SIZE = 30
SCREEN_SIZE = CELL_SIZE * GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self, color, init_pos):
        self.body = [init_pos]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = color
        self.grow = False

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
        for segment in self.body:
            pygame.draw.rect(screen, self.color,
                             pygame.Rect(segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

class Food:
    def __init__(self, snake_positions):
        self.position = self.spawn(snake_positions)

    def spawn(self, occupied):
        while True:
            pos = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            if pos not in occupied:
                return pos

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0),
                         pygame.Rect(self.position[0]*CELL_SIZE, self.position[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
