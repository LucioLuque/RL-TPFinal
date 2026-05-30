import time
import numpy as np

from platform1 import MovingPlatformLandingAviary


env = MovingPlatformLandingAviary(
    gui=True,
    platform_amp=0.0,
    platform_omega=0.5,
    ctrl_freq=24,
    max_episode_seconds=20,
)

obs, info = env.reset()

import time

t0 = time.time()

for i in range(24 * 20):
    action = np.array([0.0, 0.0, -1.0, 0.5], dtype=np.float32)

    obs, reward, terminated, truncated, info = env.step(action)

    if i % 12 == 0:
        print("step:", i, "info:", info)

    time.sleep(1 / 24)

    if terminated or truncated:
        print("Terminó:", info)
        break

t1 = time.time()
print("Tiempo total:", round(t1 - t0, 2), "segundos")

env.close()