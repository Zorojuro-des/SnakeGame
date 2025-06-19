# rl_agent/train.py
from stable_baselines3 import DQN
from rl_agent.env import SnakeEnv
import time
start = time.time()

env = SnakeEnv()
model = DQN("CnnPolicy", env, verbose=1)
model.learn(total_timesteps=100_000)
model.save("rl_agent/model")
end = time.time()
print(f"Training completed in {end - start:.2f} seconds.")