# rl_agent/env.py
import gym
from gym import spaces
import numpy as np
import random

class SnakeEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.grid_size = 10
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.grid_size, self.grid_size, 3), dtype=np.uint8)
        self.reset()

    def reset(self):
        self.snake_body = [(5, 5)]
        self.food_pos = self.spawn_food()
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        return self._get_obs()

    def spawn_food(self):
        while True:
            pos = (random.randint(0, 9), random.randint(0, 9))
            if pos not in self.snake_body:
                return pos

    def step(self, action):
        if action is not None:
            self._change_dir(action)
        head_x, head_y = self.snake_body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % 10, (head_y + dy) % 10)

        if new_head in self.snake_body:
            return self._get_obs(), -1, True, {}

        self.snake_body.insert(0, new_head)
        reward = 0
        done = False

        if new_head == self.food_pos:
            reward = 1
            self.food_pos = self.spawn_food()
        else:
            self.snake_body.pop()

        return self._get_obs(), reward, done, {}

    def _change_dir(self, action):
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        self.direction = dirs[action]

    def _get_obs(self):
        grid = np.zeros((10, 10, 3), dtype=np.uint8)
        for x, y in self.snake_body:
            grid[y][x][1] = 1  # Green channel for snake
        x, y = self.food_pos
        grid[y][x][0] = 1      # Red channel for food
        return grid
