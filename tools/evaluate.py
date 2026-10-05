"""Evalua una corrida en muchos episodios, sin ventana, y guarda el resultado en runs/<id>/.

Las evaluaciones del entrenamiento son de 8 episodios (la tasa de exito va de a 12.5 % y salta mucho).
Esto corre N episodios deterministas, siempre con las mismas semillas (seed, seed+1, ...), para que
distintas corridas se comparen sobre los mismos episodios.

    python -m tools.evaluate --load v17-lucio --best --episodes 100

Escribe runs/<id>/eval_best.json (o eval_final.json) con la tasa de exito y su intervalo, como termina
cada episodio, cuanto tarda en aterrizar y cuanto se recorta cada valor de la observacion.
"""
import json
import os
from collections import Counter
from datetime import datetime

import numpy as np
import pybullet as p
from stable_baselines3 import PPO

from run_registry import _git
from utils import get_best_model_dir, get_latest_version, get_model_path, get_run_dir, make_env, parse_args, run_tag

DEFAULT_EPISODES = 100

OBS_NAMES = [
    "rel_px", "rel_py", "rel_pz", "rel_vx", "rel_vy", "rel_vz", "roll", "pitch", "yaw",
    "wx", "wy", "wz", "vx", "vy", "vz", "prev_a0", "prev_a1", "prev_a2", "prev_a3",
]


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confianza del 95 % para una proporcion (mejor que +-1.96*sd con pocos fallos)."""
    if n == 0:
        return 0.0, 0.0
    phat = successes / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2)) / denom
    return float(center - half), float(center + half)


def crash_kind(raw_env) -> str:
    """Contra que choco: 'piso', 'plataforma' (contacto que no es base contra tope) o 'inclinacion'."""
    contacts = p.getContactPoints(bodyA=raw_env.DRONE_IDS[0], physicsClientId=raw_env.CLIENT)
    if any(c[2] != raw_env.platform_id for c in contacts):
        return "piso"
    if contacts:
        return "plataforma"
    return "inclinacion"


def run_episode(model, env, seed: int) -> tuple[dict, list]:
    raw_env = env.unwrapped
    obs, _ = env.reset(seed=seed)
    raws = []
    steps = 0
    while True:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, info = env.step(action)
        steps += 1
        raws.append(raw_env._computeRawObs())
        if terminated or truncated:
            break

    if info["is_success"]:
        outcome = "exito"
    elif info["crashed"]:
        outcome = f"choque_{crash_kind(raw_env)}"
    else:
        outcome = "tiempo"
    return {"seed": seed, "outcome": outcome, "steps": steps, "d_xy": round(info["d_xy"], 3)}, raws


def main():
    new_args = [
        ("episodes", int, DEFAULT_EPISODES, "Number of evaluation episodes."),
        ("best", bool, False, "Evaluate best/best_model.zip instead of model.zip."),
    ]
    args = parse_args(eval=True, new_args=new_args)

    run_id = args.load if args.load is not None else get_latest_version()
    if run_id is None:
        raise SystemExit("No hay corridas para evaluar.")
    which = "best" if args.best else "final"
    model_path = (
        os.path.join(get_best_model_dir(run_id), "best_model.zip") if args.best
        else get_model_path(run_id, with_extension=True)
    )

    model = PPO.load(model_path, device="cpu")
    env = make_env(gui=False, seed=args.seed)()
    ctrl_freq = env.unwrapped.CTRL_FREQ

    episodes, raws = [], []
    for i in range(args.episodes):
        ep, ep_raws = run_episode(model, env, args.seed + i)
        episodes.append(ep)
        raws.extend(ep_raws)
        print(f"\r{i + 1}/{args.episodes} episodios", end="", flush=True)
    print()
    env.close()

    outcomes = Counter(ep["outcome"] for ep in episodes)
    n_success = outcomes["exito"]
    low, high = wilson_interval(n_success, args.episodes)
    landing_s = np.array([ep["steps"] for ep in episodes if ep["outcome"] == "exito"]) / ctrl_freq

    raws = np.array(raws)
    scale = env.unwrapped._obs_scale
    clipped = (np.abs(raws / scale) > 1).mean(axis=0)
    p999 = np.percentile(np.abs(raws), 99.9, axis=0)

    result = {
        "run_id": run_tag(run_id),
        "model": which,
        "episodes": args.episodes,
        "seeds": [args.seed, args.seed + args.episodes - 1],
        "success_rate": n_success / args.episodes,
        "success_ci95": [round(low, 3), round(high, 3)],
        "outcomes": dict(outcomes),
        "landing_time_s": (
            {"median": round(float(np.median(landing_s)), 2), "p90": round(float(np.percentile(landing_s, 90)), 2)}
            if len(landing_s) else None
        ),
        "obs_clipped_fraction": {n: round(float(c), 4) for n, c in zip(OBS_NAMES, clipped)},
        "obs_abs_p999": {n: round(float(v), 3) for n, v in zip(OBS_NAMES, p999)},
        "obs_scale": {n: round(float(s), 3) for n, s in zip(OBS_NAMES, scale)},
        "git_commit": (_git("rev-parse", "HEAD") or "").strip() or None,
        "evaluated_at": datetime.now().isoformat(timespec="seconds"),
        "per_episode": episodes,
    }
    out_path = os.path.join(get_run_dir(run_id), f"eval_{which}.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"{run_tag(run_id)} ({which}): exito {100 * result['success_rate']:.1f} % "
          f"(IC 95 %: {100 * low:.1f}-{100 * high:.1f} %) en {args.episodes} episodios")
    print("Como terminan:", dict(outcomes))
    if result["landing_time_s"]:
        print(f"Tiempo hasta aterrizar: mediana {result['landing_time_s']['median']} s, "
              f"p90 {result['landing_time_s']['p90']} s")
    over = {n: f"{100 * c:.1f} %" for n, c in result["obs_clipped_fraction"].items() if c > 0.01}
    print("Valores recortados en mas del 1 % de los pasos:", over or "ninguno")
    print(f"Guardado en {out_path}")


if __name__ == "__main__":
    main()
