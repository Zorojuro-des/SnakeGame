from stable_baselines3 import DQN
from env import SnakeEnv
from stable_baselines3.common.env_checker import check_env
import time

env = SnakeEnv()
check_env(env)
start = time.time()
model = DQN("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=5_000_000)
model.save("model")
end = time.time()
print(f"Training completed in {end - start:.2f} seconds")