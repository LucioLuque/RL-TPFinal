import time
import numpy as np

from platform1 import MovingPlatformLandingAviary

# ─── Cambiá acá el modo ───────────────────────────────────────────
# MODE = "static"      # Caso 1: plataforma fija
# MODE = "linear"    # Caso 2: traslación lineal aleatoria
MODE = "turtlebot" # Caso 3: movimiento tipo turtlebot
# ─────────────────────────────────────────────────────────────────

framerate = 24
episode_duration_seconds = 20

env = MovingPlatformLandingAviary(
    mode=MODE,
    gui=True,
    ctrl_freq=framerate,
    max_episode_seconds=episode_duration_seconds,
    platform_radius=0.35,
    # Parámetros opcionales según modo:
    # linear_speed_range=(0.1, 0.4),
    turtle_linear_speed_range=(0.1, 0.3),
    turtle_angular_speed_range=(0.2, 0.8),
)

obs, info = env.reset()

for i in range(framerate * episode_duration_seconds):
    action = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    obs, reward, terminated, truncated, info = env.step(action)

    if i % framerate == 0:
        print(
            f"t: {round(i / framerate, 2)}s",
            f"| mode: {MODE}",
            f"| platform_pos: {np.round(env.platform_pos, 3)}",
            f"| platform_vel: {np.round(env.platform_vel, 3)}",
            f"| reward: {round(reward, 3)}",
        )

    time.sleep(1 / framerate)

    if terminated or truncated:
        print("── reset ──")
        obs, info = env.reset()

env.close()