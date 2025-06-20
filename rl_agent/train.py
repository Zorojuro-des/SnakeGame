# rl_agent/train.py
from stable_baselines3 import DQN
from env import SnakeEnv
import time
start = time.time()

env = SnakeEnv()
model = DQN("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100_000)
model.save("model")
end = time.time()
print(f"Training completed in {end - start:.2f} seconds.")