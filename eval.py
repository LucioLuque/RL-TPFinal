import time

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from platform1 import MovingPlatformLandingAviary


MODEL_PATH = "ppo_landing_static_platform.zip"
VECNORMALIZE_PATH = "vecnormalize_landing.pkl"


def make_env():
    env = MovingPlatformLandingAviary(
        gui=True,
        platform_amp=0.0,
        platform_omega=0.5,
        ctrl_freq=24,
        max_episode_seconds=20,
    )
    env = Monitor(env)
    env.reset(seed=42)
    return env


env = DummyVecEnv([make_env])

env = VecNormalize.load(VECNORMALIZE_PATH, env)

env.training = False
env.norm_reward = False

model = PPO.load(MODEL_PATH, env=env, device="cpu")

obs = env.reset()
episodes = 5
successful_landings = 0
for episode in range(episodes):
    while True:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)

        time.sleep(1 / 24)

        if done:
            print(f"Episodio {episode + 1} terminado")
            print("Info:", info)
            if info[0].get("is_success", False):
                successful_landings += 1
            obs = env.reset()
            break

print(f"Éxitos: {successful_landings}/{episodes}")

env.close()