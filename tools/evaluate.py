"""Evalua una corrida en muchos episodios, sin ventana, y guarda el resultado en runs/<id>/.

Las evaluaciones del entrenamiento son de 8 episodios (la tasa de exito va de a 12.5 % y salta mucho).
Esto corre N episodios deterministas, siempre con las mismas semillas (seed, seed+1, ...), para que
distintas corridas se comparen sobre los mismos episodios.

    python -m tools.evaluate --load v17-lucio --best --episodes 100

Escribe runs/<id>/eval_best.json (o eval_final.json) con la tasa de exito y su intervalo, como termina
cada episodio, cuanto tarda en aterrizar, que tan centrado aterriza (`landing`), como toca la plataforma
(`touchdown`), que tan suave vuela (`smoothness`) y cuanto se recorta cada valor de la observacion.
"""
import json
import os
from collections import Counter
from datetime import datetime

import numpy as np
import pybullet as p
from stable_baselines3 import PPO

from run_registry import _git
from utils import get_best_model_dir, get_latest_version, get_model_path, get_run_dir, make_env, parse_args, run_reward, run_tag

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


def commanded_velocity(raw_env, action) -> np.ndarray:
    """Velocidad que se le pide al dron (m/s): la cuenta del entorno, que depende de action_mode."""
    return raw_env._commanded_velocity(action)


def run_episode(model, env, seed: int) -> tuple[dict, list, dict]:
    """Corre un episodio. Ademas del resultado, devuelve cuanto cambia la accion entre pasos (suavidad)."""
    raw_env = env.unwrapped
    obs, _ = env.reset(seed=seed)
    raws = []
    steps = 0
    actions, cmd_vels, drone_vels = [], [], []
    touchdown = None  # como llega al primer contacto (cualquiera)
    prev_raw = None
    bounces = 0       # veces que deja de tocar el tope despues de haberlo tocado
    was_on_top = False
    while True:
        action, _ = model.predict(obs, deterministic=True)
        action = np.clip(action, env.action_space.low, env.action_space.high)
        obs, _, terminated, truncated, info = env.step(action)
        steps += 1
        raw = raw_env._computeRawObs()
        raws.append(raw)
        actions.append(action)
        cmd_vels.append(commanded_velocity(raw_env, action))
        drone_vels.append(raw[12:15])
        contact = raw_env._contact
        if contact is not None and touchdown is None:
            # Velocidad e inclinacion del ultimo paso sin contacto: al final del paso con contacto, el choque ya freno
            # al dron en los pasos de fisica (v67 llega a 0.51 m/s y al final de ese paso marca ~0).
            before = prev_raw if prev_raw is not None else raw
            touchdown = {
                "contact": contact,
                # velocidad vertical relativa a la plataforma justo antes de tocar (m/s, positiva = bajando)
                "vz": round(float(-before[5]), 3),
                # inclinacion justo antes de tocar: max(|roll|, |pitch|) en grados
                "tilt_deg": round(float(np.degrees(np.max(np.abs(before[6:8])))), 2),
                "d_xy": round(float(np.linalg.norm(raw[0:2])), 3),
            }
        prev_raw = raw
        on_top = contact == "top"
        if was_on_top and not on_top and not terminated:
            bounces += 1
        was_on_top = on_top
        if terminated or truncated:
            break
    smooth = {}
    if steps > 2:
        freq = raw_env.CTRL_FREQ
        raws_ep = np.array(raws)
        accel = np.diff(drone_vels, axis=0) * freq
        cmd_change = np.linalg.norm(np.diff(cmd_vels, axis=0), axis=1)
        smooth = {
            # sum((a - a_anterior)^2), lo mismo que castiga reward_action_coef
            "action_change": float(np.mean(np.sum(np.diff(actions, axis=0) ** 2, axis=1))),
            # cuanto cambia la velocidad pedida por paso (m/s)
            "cmd_vel_change": float(np.mean(cmd_change)),
            # percentil 95 del cambio de velocidad pedida: los saltos grandes, que el promedio esconde
            "cmd_vel_change_p95": float(np.percentile(cmd_change, 95)),
            # aceleracion real del dron (m/s^2)
            "drone_accel": float(np.mean(np.linalg.norm(accel, axis=1))),
            # jerk real del dron (m/s^3): cuanto cambia la aceleracion
            "drone_jerk": float(np.mean(np.linalg.norm(np.diff(accel, axis=0), axis=1)) * freq),
            # inclinacion RMS en el episodio (grados): sqrt(mean(roll^2 + pitch^2))
            "tilt_rms_deg": float(np.degrees(np.sqrt(np.mean(np.sum(raws_ep[:, 6:8] ** 2, axis=1))))),
            # velocidad angular RMS de roll y pitch (rad/s): bamboleo
            "ang_vel_rms": float(np.sqrt(np.mean(np.sum(raws_ep[:, 9:11] ** 2, axis=1)))),
        }

    if info["is_success"]:
        outcome = "exito"
    elif info["crashed"]:
        outcome = f"choque_{crash_kind(raw_env)}"
    else:
        outcome = "tiempo"
    ep = {"seed": seed, "outcome": outcome, "steps": steps, "d_xy": round(info["d_xy"], 3),
          "touchdown": touchdown, "bounces": bounces}
    return ep, raws, smooth


def landing_summary(episodes: list) -> dict | None:
    """Que tan centrado aterriza: distancia horizontal al centro de la plataforma (m) en los aterrizajes."""
    d = np.array([ep["d_xy"] for ep in episodes if ep["outcome"] == "exito"])
    if not len(d):
        return None
    return {
        "d_xy_mean": round(float(d.mean()), 3),
        "d_xy_median": round(float(np.median(d)), 3),
        "d_xy_p90": round(float(np.percentile(d, 90)), 3),
        "within_5cm": round(float((d < 0.05).mean()), 3),
        "within_10cm": round(float((d < 0.10).mean()), 3),
    }


def touchdown_summary(episodes: list) -> dict | None:
    """Como llega a la plataforma la primera vez (ultimo paso antes del contacto), en los episodios en que el primer
    contacto es base contra tope."""
    tds = [ep["touchdown"] for ep in episodes if ep["touchdown"] and ep["touchdown"]["contact"] == "top"]
    if not tds:
        return None
    vz = np.array([t["vz"] for t in tds])
    tilt = np.array([t["tilt_deg"] for t in tds])
    return {
        "n": len(tds),
        "vz_median": round(float(np.median(vz)), 3),
        "vz_p90": round(float(np.percentile(vz, 90)), 3),
        "tilt_deg_median": round(float(np.median(tilt)), 2),
        "tilt_deg_p90": round(float(np.percentile(tilt, 90)), 2),
        # rebotes por episodio (despega del tope despues de tocarlo), en los episodios que aterrizan
        "bounces_mean": round(float(np.mean([ep["bounces"] for ep in episodes if ep["outcome"] == "exito"] or [0])), 2),
    }


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
    env = make_env(gui=False, seed=args.seed, reward=run_reward(run_id))()
    ctrl_freq = env.unwrapped.CTRL_FREQ

    episodes, raws, smooths = [], [], []
    for i in range(args.episodes):
        ep, ep_raws, smooth = run_episode(model, env, args.seed + i)
        episodes.append(ep)
        raws.extend(ep_raws)
        if smooth:
            smooths.append(smooth)
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
        # Aterrizajes: distancia al centro de la plataforma (m)
        "landing": landing_summary(episodes),
        # Primer contacto con el tope: velocidad de bajada e inclinacion justo antes de tocar, y rebotes
        "touchdown": touchdown_summary(episodes),
        # Promedio por episodio de cuanto cambia la accion entre pasos y de cuanto se mueve el dron (mas chico = mas suave)
        "smoothness": {k: round(float(np.mean([s[k] for s in smooths])), 4) for k in smooths[0]} if smooths else None,
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
    if result["landing"]:
        print("Aterrizaje (distancia al centro, m):", result["landing"])
    if result["touchdown"]:
        print("Primer contacto con el tope:", result["touchdown"])
    if result["smoothness"]:
        print("Suavidad (promedio por episodio):", result["smoothness"])
    over = {n: f"{100 * c:.1f} %" for n, c in result["obs_clipped_fraction"].items() if c > 0.01}
    print("Valores recortados en mas del 1 % de los pasos:", over or "ninguno")
    print(f"Guardado en {out_path}")


if __name__ == "__main__":
    main()
