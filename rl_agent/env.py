import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random

class SnakeEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.grid_size = 30
        self.action_space = spaces.Discrete(4)  # 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        self.observation_space = spaces.Box(low=0, high=1, shape=(30, 30, 4), dtype=np.uint8)
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.snake_body = [(5, 5)]
        self.human_body = [(10, 10), (10, 11)]
        self.direction = (1, 0)
        self.food_pos = self._place_food()
        return self._get_obs(), {}

    def _place_food(self):
        while True:
            pos = (random.randint(0, 23), random.randint(0, 23))
            if pos not in self.snake_body and pos not in self.human_body:
                return pos

    def step(self, action):
        self._set_direction(action)
        head_x, head_y = self.snake_body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % self.grid_size, (head_y + dy) % self.grid_size)

        reward = 0
        terminated = False

        if new_head in self.snake_body:
            reward = -10
            terminated = True
        elif new_head in self.human_body:
            reward = -15
            terminated = True

        self.snake_body.insert(0, new_head)

        if new_head == self.food_pos:
            reward = 10
            self.food_pos = self._place_food()
        else:
            self.snake_body.pop()

        dist = self._manhattan_dist(new_head, self.food_pos)
        reward += 0.1 * (1.0 - dist / (2 * self.grid_size))

        return self._get_obs(), reward, terminated, False, {}

    def _manhattan_dist(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _set_direction(self, action):
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # UP, DOWN, LEFT, RIGHT
        self.direction = dirs[action]

    def _get_obs(self):
        obs = np.zeros((self.grid_size, self.grid_size, 4), dtype=np.uint8)

        # Channel 0: Food
        fx, fy = self.food_pos
        obs[fy, fx, 0] = 1

        # Channel 1: Agent snake
        for x, y in self.snake_body:
            obs[y, x, 1] = 1

        # Channel 2: Human snake
        for x, y in self.human_body:
            obs[y, x, 2] = 1

        # Channel 3: Agent head
        x, y = self.snake_body[0]
        obs[y, x, 3] = 1

        return obs

    def update_human(self, body):
        self.human_body = body
