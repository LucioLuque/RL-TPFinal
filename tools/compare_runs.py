"""Tabla comparativa de corridas (markdown) y grafico de la tasa de exito del entrenamiento.

    python -m tools.compare_runs v21-lucio v23-lucio v24-lucio --plot media/plots/recompensas.png

Por corrida: variante de recompensa, seed, rollout/success_rate (promedio en una ventana alrededor de 0.5M,
1.0M y 1.5M pasos), primer paso con >= 50 %, y la evaluacion de 100 episodios del best (eval_best.json):
exito, como terminan, tiempo hasta aterrizar y suavidad.
"""
import argparse
import glob
import json
import os

import numpy as np
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

from utils import get_run_dir, run_tag

CHECKPOINTS = [500_000, 1_000_000, 1_500_000]
WINDOW = 100_000  # promedio de rollout/success_rate en [t - WINDOW, t]


def load_curve(run_id, tag="rollout/success_rate"):
    dirs = sorted(glob.glob(os.path.join(get_run_dir(run_id), "tb", "*")))
    steps, values = [], []
    for d in dirs:
        ea = EventAccumulator(d, size_guidance={"scalars": 0})
        ea.Reload()
        if tag in ea.Tags().get("scalars", []):
            for e in ea.Scalars(tag):
                steps.append(e.step)
                values.append(e.value)
    order = np.argsort(steps)
    return np.array(steps)[order], np.array(values)[order]


def summarize(run_id):
    run_dir = get_run_dir(run_id)
    with open(os.path.join(run_dir, "run.json")) as f:
        run = json.load(f)
    session = run["sessions"][0]
    args = session["args"]
    row = {"run": run_tag(run_id), "reward": args.get("reward") or "base", "seed": args["seed"]}

    steps, values = load_curve(run_id)
    for t in CHECKPOINTS:
        mask = (steps > t - WINDOW) & (steps <= t)
        row[f"sr_{t // 1000}k"] = float(values[mask].mean()) if mask.any() else None
    over = steps[values >= 0.5]
    row["first_50"] = int(over[0]) if len(over) else None

    eval_path = os.path.join(run_dir, "eval_best.json")
    if os.path.exists(eval_path):
        with open(eval_path) as f:
            ev = json.load(f)
        row["eval"] = ev["success_rate"]
        row["ci"] = ev["success_ci95"]
        row["outcomes"] = ev["outcomes"]
        row["landing"] = (ev.get("landing_time_s") or {}).get("median")
        row["smooth"] = ev.get("smoothness")
    row["best_at"] = session["results"].get("best_at_timesteps") if session.get("results") else None
    return row


def pct(x):
    return "–" if x is None else f"{100 * x:.0f}%"


def to_markdown(rows):
    head = ("| Run | Recompensa | Seed | Éxito entr. 0.5M / 1M / 1.5M | Cruza 50 % | Best a | Éxito best (100 ep.) "
            "| Choque plat. / piso / tiempo | Aterriza (s) | Δacción | Δv pedida (m/s) |")
    lines = [head, "|---" * 11 + "|"]
    for r in rows:
        sr = " / ".join(pct(r[f"sr_{t // 1000}k"]) for t in CHECKPOINTS)
        first = f"{r['first_50'] / 1e6:.2f}M" if r["first_50"] else "nunca"
        best_at = f"{r['best_at'] / 1e6:.1f}M" if r.get("best_at") else "–"
        if "eval" in r:
            ev = f"{pct(r['eval'])} ({100 * r['ci'][0]:.0f}–{100 * r['ci'][1]:.0f})"
            o = r["outcomes"]
            fails = f"{o.get('choque_plataforma', 0)} / {o.get('choque_piso', 0)} / {o.get('tiempo', 0)}"
            land = r["landing"] if r["landing"] is not None else "–"
            sm = r.get("smooth") or {}
            da = f"{sm['action_change']:.2f}" if sm else "–"
            dv = f"{sm['cmd_vel_change']:.3f}" if sm else "–"
        else:
            ev = fails = land = da = dv = "–"
        lines.append(f"| {r['run']} | `{r['reward']}` | {r['seed']} | {sr} | {first} | {best_at} | {ev} | {fails} "
                     f"| {land} | {da} | {dv} |")
    return "\n".join(lines)


def plot(run_ids, out_path, smooth=10):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 5))
    for run_id in run_ids:
        steps, values = load_curve(run_id)
        if len(values) == 0:
            continue
        k = min(smooth, len(values))
        values = np.convolve(values, np.ones(k) / k, mode="valid")
        steps = steps[k - 1:]
        reward = summarize(run_id)["reward"]
        ax.plot(steps / 1e6, 100 * values, label=f"{run_tag(run_id)} ({reward})")
    ax.set_xlabel("Pasos (M)")
    ax.set_ylabel("rollout/success_rate (%)")
    ax.set_ylim(0, 100)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    print(f"Grafico en {out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+")
    parser.add_argument("--plot", default=None, help="Ruta del png con las curvas de exito.")
    args = parser.parse_args()
    print(to_markdown([summarize(r) for r in args.runs]))
    if args.plot:
        plot(args.runs, args.plot)


if __name__ == "__main__":
    main()
