"""Cuanto satura la accion una politica (modelo final, 20 episodios): python -m tools.action_saturation v40-lucio v42-lucio"""
import sys; sys.path.insert(0, '.')
import numpy as np
from stable_baselines3 import PPO
from utils import make_env
for rid in sys.argv[1:]:
    model = PPO.load(f'runs/{rid}/model.zip', device='cpu')
    env = make_env(False, 0)(); acts = []; raw_means = []
    for seed in range(42, 62):
        obs, _ = env.reset(seed=seed)
        while True:
            a, _ = model.predict(obs, deterministic=True)
            import torch
            with torch.no_grad():
                m = model.policy.get_distribution(model.policy.obs_to_tensor(obs)[0]).distribution.mean.numpy()[0]
            raw_means.append(m); acts.append(a)
            obs, _, te, tr, _ = env.step(a)
            if te or tr: break
    acts = np.array(acts); raw = np.array(raw_means)
    sat = (np.abs(acts[:, :3]) > 0.99).mean(axis=0)
    s_one = (acts[:, 3] > 0.99).mean()
    allsat = (np.abs(acts[:, :3]) > 0.99).all(axis=1).mean()
    print(f"{rid}: saturadas dx,dy,dz = {np.round(sat,2)}, s=1: {s_one:.2f}, las 3 direcciones saturadas: {allsat:.2f}, "
          f"|media gaussiana| mediana = {np.round(np.median(np.abs(raw),axis=0),2)}")
