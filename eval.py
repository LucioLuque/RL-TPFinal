import time

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

from tools.evaluate import commanded_velocity
from utils import DEFAULT_CTRL_FREQ, parse_args, get_model_path, get_latest_version, make_env, run_reward, set_global_seeds

DEFAULT_EVAL_EPISODES = 5


def stats(name: str, values: list, unit: str, fmt: str = "{:.2f}") -> str:
    """'name: min / promedio / max' de una lista, o un aviso si esta vacia."""
    if not values:
        return f"{name}: sin datos"
    f = lambda x: fmt.format(x)
    return f"{name} (min / promedio / max): {f(min(values))} / {f(np.mean(values))} / {f(max(values))} {unit}"


def main():
    #python eval.py --load 4 --seed 42 --episodes 5

    new_args = [
        ("episodes", int, DEFAULT_EVAL_EPISODES, "Number of evaluation episodes."),
    ]
    args = parse_args(eval=True, new_args=new_args)
    set_global_seeds(args.seed)

    # --load
    version = args.load if args.load is not None else get_latest_version()
    if version is None:
        raise SystemExit("No saved weights found to evaluate. Train a model first.")

    model_path = get_model_path(version, with_extension=True)

    env = DummyVecEnv([make_env(gui=True, seed=args.seed, reward=run_reward(version))])
    raw_env = env.envs[0].unwrapped

    model = PPO.load(model_path, env=env, device="cpu")

    env.seed(args.seed)
    obs = env.reset()
    successful_landings = 0
    centers, landing_times, smoothness = [], [], []

    for episode in range(args.episodes):
        steps = 0
        cmd_vels = []
        while True:
            action, _ = model.predict(obs, deterministic=True)
            cmd_vels.append(commanded_velocity(raw_env, action[0]))
            obs, reward, done, info = env.step(action)
            steps += 1

            time.sleep(1 / DEFAULT_CTRL_FREQ)

            if done:
                # info es el del ultimo paso del episodio (DummyVecEnv ya reseteo el entorno)
                info = info[0]
                seconds = steps / DEFAULT_CTRL_FREQ
                # cuanto salta la velocidad pedida por paso (m/s), como cmd_vel_change en tools/evaluate.py
                cmd_change = float(np.mean(np.linalg.norm(np.diff(cmd_vels, axis=0), axis=1))) if steps > 1 else 0.0
                smoothness.append(cmd_change)
                if info.get("is_success", False):
                    successful_landings += 1
                    centers.append(100 * info["d_xy"])
                    landing_times.append(seconds)
                    result = f"aterrizo a {100 * info['d_xy']:.1f} cm del centro en {seconds:.2f} s"
                elif info.get("crashed", False):
                    result = f"choco a los {seconds:.2f} s"
                else:
                    result = f"se acabo el tiempo ({seconds:.0f} s)"
                print(f"Episodio {episode + 1}: {result}; salto medio de velocidad pedida {cmd_change:.3f} m/s")
                obs = env.reset()
                break

    print(f"\nÉxitos: {successful_landings}/{args.episodes}")
    print(stats("Distancia al centro al aterrizar", centers, "cm", "{:.1f}"))
    print(stats("Tiempo hasta aterrizar", landing_times, "s"))
    print(stats("Salto medio de velocidad pedida por paso (mas chico = mas suave)", smoothness, "m/s", "{:.3f}"))
    env.close()

if __name__ == "__main__":
    main()
