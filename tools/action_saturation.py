"""Cuanto satura la accion una politica: fraccion de pasos con cada componente en el borde y media de la gaussiana.

    python -m tools.action_saturation v40-lucio v42-lucio --episodes 20

Modelo final, determinista, episodios con seeds 42, 43, ... "Saturada" = |a| > 0.99 despues del recorte. Una media
de la gaussiana muy afuera de [-1, 1] quiere decir que la politica no usa valores intermedios en ese eje (ver
docs/pruebas-recompensas-2026-10-15.md, "las politicas son bang-bang").
"""
import argparse

import numpy as np
import torch
from stable_baselines3 import PPO

from utils import get_model_path, make_env, run_reward


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="+")
    parser.add_argument("--episodes", type=int, default=20)
    args = parser.parse_args()

    for rid in args.runs:
        model = PPO.load(get_model_path(rid, with_extension=True), device="cpu")
        env = make_env(False, 0, run_reward(rid))()
        actions, means = [], []
        for seed in range(42, 42 + args.episodes):
            obs, _ = env.reset(seed=seed)
            while True:
                action, _ = model.predict(obs, deterministic=True)
                with torch.no_grad():
                    dist = model.policy.get_distribution(model.policy.obs_to_tensor(obs)[0])
                means.append(dist.distribution.mean.numpy()[0])
                actions.append(action)
                obs, _, terminated, truncated, _ = env.step(action)
                if terminated or truncated:
                    break
        env.close()
        actions, means = np.array(actions), np.array(means)
        sat = (np.abs(actions[:, :3]) > 0.99).mean(axis=0)
        print(f"{rid}: saturadas dx, dy, dz = {np.round(sat, 2)}, s = 1: {(actions[:, 3] > 0.99).mean():.2f}, "
              f"las 3 direcciones saturadas: {(np.abs(actions[:, :3]) > 0.99).all(axis=1).mean():.2f}, "
              f"mediana de |media gaussiana| (dx, dy, dz, s) = {np.round(np.median(np.abs(means), axis=0), 2)}")


if __name__ == "__main__":
    main()
