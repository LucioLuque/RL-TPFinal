"""Registro de corridas de entrenamiento.

Cada corrida deja en runs/<run_id>/ lo necesario para saber, despues, con que codigo y configuracion
se entreno y que resultado dio, aunque el codigo se haya cambiado sin commitear:

- run.json: args, hiperparametros, entorno, commit de git y resultados de cada sesion de entrenamiento.
- diff.patch: cambios sin commitear respecto del commit (se entreno con HEAD + este diff).
- env.py / levels.yaml: copia del entorno (reward, obs) y de los niveles usados.

Continuar una corrida con --load agrega una sesion nueva a run.json; sus archivos llevan sufijo _s<k>.
"""
import json
import os
import shutil
import subprocess
import time
from datetime import datetime

from utils import LEVEL, get_author, get_run_dir, run_tag


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def _git_info() -> tuple[dict | None, str]:
    commit = _git("rev-parse", "HEAD")
    if commit is None:
        return None, ""
    diff = _git("diff", "HEAD") or ""
    untracked = [
        path for path in (_git("ls-files", "--others", "--exclude-standard") or "").splitlines()
        if not path.startswith("runs/")
    ]
    info = {
        "commit": commit.strip(),
        "branch": (_git("rev-parse", "--abbrev-ref", "HEAD") or "").strip(),
        "dirty": bool(diff),
        "untracked": untracked,
    }
    return info, diff


def _schedule_value(value):
    # SB3 convierte clip_range (y a veces learning_rate) en funciones del progreso restante.
    return value(1.0) if callable(value) else value


def _hyperparams(model) -> dict:
    return {
        "algo": type(model).__name__,
        "learning_rate": _schedule_value(model.learning_rate),
        "n_steps": model.n_steps,
        "batch_size": model.batch_size,
        "n_epochs": model.n_epochs,
        "gamma": model.gamma,
        "gae_lambda": model.gae_lambda,
        "ent_coef": model.ent_coef,
        "vf_coef": model.vf_coef,
        "clip_range": _schedule_value(model.clip_range),
        "max_grad_norm": model.max_grad_norm,
        "policy_kwargs": model.policy_kwargs,
        "n_envs": model.n_envs,
    }


def previous_best(run_id) -> dict | None:
    """Mejor checkpoint registrado de una corrida (el que esta en runs/<run_id>/best/), o None.

    Cada sesion arrastra el mejor de las anteriores, asi que alcanza con la ultima que tenga uno.
    """
    path = os.path.join(get_run_dir(run_id), "run.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        sessions = json.load(f)["sessions"]
    for session in reversed(sessions):
        results = session.get("results") or {}
        if results.get("best_at_timesteps") is not None:
            return results
    return None


class RunRecord:
    def __init__(self, run_id, args: dict, model, env_kwargs: dict, obs_dim: int):
        self.dir = get_run_dir(run_id)
        self.path = os.path.join(self.dir, "run.json")
        os.makedirs(self.dir, exist_ok=True)

        if os.path.exists(self.path):
            with open(self.path) as f:
                self.data = json.load(f)
        else:
            self.data = {"run_id": run_tag(run_id), "sessions": []}

        k = len(self.data["sessions"]) + 1
        suffix = "" if k == 1 else f"_s{k}"
        git, diff = _git_info()

        files = {}
        if diff:
            files["diff"] = f"diff{suffix}.patch"
            with open(os.path.join(self.dir, files["diff"]), "w") as f:
                f.write(diff)
        for src in ("env.py", "levels.yaml"):
            name, ext = os.path.splitext(src)
            files[name] = f"{name}{suffix}{ext}"
            shutil.copyfile(src, os.path.join(self.dir, files[name]))

        self._t0 = time.time()
        self.session = {
            "session": k,
            "author": get_author(),
            "status": "running",
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "start_timesteps": model.num_timesteps,
            "args": args,
            "hyperparams": _hyperparams(model),
            "level": LEVEL,
            "env_kwargs": env_kwargs,
            "obs_dim": obs_dim,
            "git": git,
            "files": files,
            "results": None,
        }
        self.data["sessions"].append(self.session)
        self.save()

    def finish(self, status: str, model, eval_callback=None):
        self.session["status"] = status
        self.session["finished_at"] = datetime.now().isoformat(timespec="seconds")
        self.session["duration_s"] = round(time.time() - self._t0, 1)

        results = {"final_timesteps": model.num_timesteps}
        if eval_callback is not None:
            results.update(eval_callback.summary())
        self.session["results"] = results
        self.save()

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False, default=str)
