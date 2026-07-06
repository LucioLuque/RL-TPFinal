import os
import time

import numpy as np
import matplotlib.pyplot as plt

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from utils import DEFAULT_CTRL_FREQ, parse_args, get_model_path, get_vecnormalize_path, get_latest_version, make_env, set_global_seeds

DEFAULT_SAVE_PATH = "plots/trajectory.png"

def unwrap_env(vec_env):
    return vec_env.venv.envs[0].unwrapped

def main():
    new_args = [
        ("out", str, DEFAULT_SAVE_PATH, "Path to save the trajectory plot."),
    ]
    args = parse_args(eval=True, new_args=new_args)
    set_global_seeds(args.seed)

    version = args.load if args.load is not None else get_latest_version()
    if version is None:
        raise SystemExit("No saved weights found to evaluate.")

    model_path = get_model_path(version, with_extension=True)
    vecnormalize_path = get_vecnormalize_path(version)

    env = DummyVecEnv([make_env(gui=True, seed=args.seed)])
    env = VecNormalize.load(vecnormalize_path, env)
    env.training = False
    env.norm_reward = False

    env.seed(args.seed)
    obs = env.reset()

    model = PPO.load(model_path, env=env, device="cpu")
    raw_env = unwrap_env(env)

    recorded = {"drone_pos": None, "platform_pos": None}
    orig_step = raw_env.step

    def step_and_record(action):
        result = orig_step(action)
        recorded["drone_pos"] = raw_env._getDroneStateVector(0)[0:3].copy()
        recorded["platform_pos"] = np.array([raw_env.platform_pos[0], raw_env.platform_pos[1], raw_env.platform_height])
        return result

    raw_env.step = step_and_record

    # obs = env.reset()

    drone_traj = [raw_env._getDroneStateVector(0)[0:3].copy()]
    platform_traj = [np.array([raw_env.platform_pos[0], raw_env.platform_pos[1], raw_env.platform_height])]

    is_success = False
    is_crashed = False

    while True:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)

        time.sleep(1 / DEFAULT_CTRL_FREQ)

        drone_traj.append(recorded["drone_pos"])
        platform_traj.append(recorded["platform_pos"])

        if done:
            is_success = info[0].get("is_success", False)
            is_crashed = info[0].get("crashed", False)
            print(f"Episodio terminado. Éxito: {is_success} | Choque: {is_crashed}")
            break

    env.close()

    drone_traj = np.array(drone_traj)
    platform_traj = np.array(platform_traj)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot(drone_traj[:, 0], drone_traj[:, 1], drone_traj[:, 2], color="blue", label="Dron")
    ax.plot(platform_traj[:, 0], platform_traj[:, 1], platform_traj[:, 2], color="red", linestyle="--", label="Plataforma")

    end_color = "green" if is_success else ("black" if is_crashed else "orange")
    ax.scatter(*drone_traj[-1], color=end_color, marker="s", s=40, label="Fin del episodio")

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.legend()

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    plt.tight_layout()
    plt.savefig(args.out, dpi=150)
    plt.show()

    print(f"Plot guardado en {args.out}")

if __name__ == "__main__":
    main()