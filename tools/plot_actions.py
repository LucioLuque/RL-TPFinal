"""Grafica la velocidad pedida (vx, vy, vz) paso a paso en algunos episodios, para comparar la suavidad de corridas.

    python -m tools.plot_actions v40-lucio v42-lucio --episodes 42 43 44 --out media/plots/accion_base_vs_suave.png

Una fila por episodio y una columna por corrida (modelo final, determinista).
"""
import argparse

import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3 import PPO

from tools.evaluate import commanded_velocity
from utils import get_model_path, make_env, run_reward


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="+")
    parser.add_argument("--episodes", type=int, nargs="+", default=[42, 43, 44], help="Seeds de los episodios.")
    parser.add_argument("--out", default="media/plots/acciones.png")
    args = parser.parse_args()

    fig, axes = plt.subplots(len(args.episodes), len(args.runs), figsize=(5.5 * len(args.runs), 3.2 * len(args.episodes)),
                             sharey=True, squeeze=False)
    for col, rid in enumerate(args.runs):
        model = PPO.load(get_model_path(rid, with_extension=True), device="cpu")
        reward = run_reward(rid)
        env = make_env(False, 0, reward)()
        raw = env.unwrapped
        for row, seed in enumerate(args.episodes):
            obs, _ = env.reset(seed=seed)
            vs = []
            while True:
                a, _ = model.predict(obs, deterministic=True)
                obs, _, terminated, truncated, info = env.step(a)
                vs.append(commanded_velocity(raw, a))
                if terminated or truncated:
                    break
            vs = np.array(vs)
            t = np.arange(len(vs)) / raw.CTRL_FREQ
            ax = axes[row, col]
            for i, c in enumerate("xyz"):
                ax.plot(t, vs[:, i], label=f"v{c} pedida")
            result = "aterriza" if info["is_success"] else ("choca" if info["crashed"] else "tiempo")
            ax.set_title(f"{rid} ({reward}), episodio seed {seed}: {result}", fontsize=9)
            ax.set_xlabel("s")
            ax.grid(alpha=0.3)
        env.close()
    axes[0, 0].set_ylabel("m/s")
    axes[0, 0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(args.out, dpi=110)
    print(f"Grafico en {args.out}")


if __name__ == "__main__":
    main()
