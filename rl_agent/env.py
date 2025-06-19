# rl_agent/env.py
import gym
from gym import spaces
import numpy as np
import random

class SnakeEnv(gym.Env):
    def __init__(self):
        super().__init__()

        self.grid_size = 30  # 30x30 grid
        self.action_space = spaces.Discrete(4)  # 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        self.observation_space = spaces.Box(
            low=0, high=1,
            shape=(self.grid_size, self.grid_size, 3),
            dtype=np.uint8
        )
        self.reset()

    def reset(self):
        self.snake_body = [(self.grid_size // 2, self.grid_size // 2)]
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])  # random start direction
        self.food_pos = self.spawn_food()
        return self._get_obs()

    def spawn_food(self):
        while True:
            pos = (
                random.randint(0, self.grid_size - 1),
                random.randint(0, self.grid_size - 1)
            )
            if pos not in self.snake_body:
                return pos

    def step(self, action):
        # Optional: ignore None action
        if action is not None:
            self._change_direction(action)

        head_x, head_y = self.snake_body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % self.grid_size, (head_y + dy) % self.grid_size)

        # Check collision with self
        if new_head in self.snake_body:
            return self._get_obs(), -1, True, {}  # reward, done, info

        self.snake_body.insert(0, new_head)

        if new_head == self.food_pos:
            reward = 1
            self.food_pos = self.spawn_food()
        else:
            self.snake_body.pop()
            reward = -0.01  # small penalty per step to encourage faster eating

        done = False
        return self._get_obs(), reward, done, {}

    def _change_direction(self, action):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # UP, DOWN, LEFT, RIGHT
        proposed = directions[action]

        # Prevent reversing directly
        if len(self.snake_body) > 1:
            if (proposed[0] * -1, proposed[1] * -1) == self.direction:
                return  # ignore reverse
        self.direction = proposed

    def _get_obs(self):
        obs = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)

        # Snake body: green channel
        for x, y in self.snake_body:
            obs[y, x, 1] = 1

        # Food: red channel
        fx, fy = self.food_pos
        obs[fy, fx, 0] = 1

        return obs
