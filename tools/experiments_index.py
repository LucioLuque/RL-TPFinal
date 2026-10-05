"""Regenera EXPERIMENTS.md: una fila por corrida, a partir de runs/*/run.json y runs/*/NOTES.md.

Se genera siempre de cero, asi que si git marca conflicto en EXPERIMENTS.md alcanza con correr
`python -m tools.experiments_index` de nuevo despues del merge.
"""
import glob
import json
import os
import re

RUNS_DIR = "runs"  # mismo que utils.RUNS_DIR; no se importa para no depender de pybullet

OUT_PATH = "EXPERIMENTS.md"
HEADER = """# Experimentos

Indice generado por `python -m tools.experiments_index` (no editar a mano). El detalle de cada corrida
esta en `runs/<run_id>/NOTES.md` (escrito con `/registrar-corrida`) y `runs/<run_id>/run.json`.

| Run | Autor | Fecha | Estado | Timesteps | Éxito best (100 ep.) | Best éxito (8 ep.) | Best reward | Cambio |
|---|---|---|---|---|---|---|---|---|
"""


def _run_number(run_id: str) -> int:
    match = re.search(r"(\d+)", run_id)
    return int(match.group(1)) if match else -1


def _change_line(run_dir: str) -> str:
    """Primera linea 'Cambio: ...' de NOTES.md, o vacio si la corrida no se registro todavia."""
    path = os.path.join(run_dir, "NOTES.md")
    if not os.path.exists(path):
        return "_sin registrar_"
    with open(path) as f:
        for line in f:
            match = re.match(r"\**Cambio:?\**:?\s*(.*)", line.strip())
            if match:
                return match.group(1).replace("|", "\\|")
    return ""


def _eval_cell(run_dir: str) -> str:
    """Exito del best en la evaluacion larga (tools/evaluate.py), con su intervalo del 95 %."""
    path = os.path.join(run_dir, "eval_best.json")
    if not os.path.exists(path):
        return "-"
    with open(path) as f:
        ev = json.load(f)
    low, high = ev["success_ci95"]
    return f"{100 * ev['success_rate']:.0f}% ({100 * low:.0f}–{100 * high:.0f})"


def _row(run_dir: str) -> tuple[int, str, str]:
    with open(os.path.join(run_dir, "run.json")) as f:
        data = json.load(f)
    sessions = data["sessions"]
    last = sessions[-1]
    results = last.get("results") or {}

    success = results.get("best_success_rate")
    reward = results.get("best_mean_reward")
    timesteps = results.get("final_timesteps")
    run_id = data["run_id"]
    status = last["status"] + (f" ({len(sessions)} sesiones)" if len(sessions) > 1 else "")

    row = "| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
        f"[{run_id}]({run_dir}/)",
        last.get("author", ""),
        sessions[0]["started_at"][:10],
        status,
        f"{timesteps:,}" if timesteps is not None else "-",
        _eval_cell(run_dir),
        f"{100 * success:.0f}%" if success is not None else "-",
        f"{reward:.2f}" if reward is not None else "-",
        _change_line(run_dir),
    )
    return _run_number(run_id), sessions[0]["started_at"], row


def main():
    run_dirs = [os.path.dirname(p) for p in glob.glob(os.path.join(RUNS_DIR, "*", "run.json"))]
    rows = sorted(_row(d) for d in run_dirs)
    with open(OUT_PATH, "w") as f:
        f.write(HEADER + "".join(row + "\n" for _, _, row in rows))
    print(f"{OUT_PATH}: {len(rows)} corridas")


if __name__ == "__main__":
    main()
