import argparse
import glob
import os
import random
import re
import subprocess
import unicodedata
import torch
import numpy as np
import yaml

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.utils import set_random_seed

from env import MovingPlatformLandingAviary

DEFAULT_CTRL_FREQ = 24
DEFAULT_MAX_EPISODE_SECONDS = 20
DEFAULT_SEED = 42
LEVEL = "turtlebot_hard_fixed"
RUNS_DIR = "runs"
RUN_TAG_RE = re.compile(r"^(?:version_|v)(\d+)(?:-[a-z0-9]+)?$")

def run_tag(run_id) -> str:
    """Nombre en disco de una corrida.

    Las corridas viejas se identifican solo con un numero (15 -> version_15); las nuevas con
    numero y autor (v16-lucio), para que dos personas entrenando en paralelo no se pisen.
    """
    run_id = str(run_id)
    return f"version_{run_id}" if run_id.isdigit() else run_id

def get_run_dir(run_id) -> str:
    return os.path.join(RUNS_DIR, run_tag(run_id))

def get_model_path(run_id, with_extension: bool = False) -> str:
    base = os.path.join(get_run_dir(run_id), "model")
    if with_extension:
        return f"{base}.zip"
    return base

def get_best_model_dir(run_id) -> str:
    return os.path.join(get_run_dir(run_id), "best")

def get_log_dir(run_id) -> str:
    return os.path.join(get_run_dir(run_id), "tb")

def _run_number(tag: str) -> int | None:
    match = RUN_TAG_RE.match(tag)
    return int(match.group(1)) if match else None

def _saved_runs() -> list[tuple[int, float, str]]:
    """(numero, mtime, tag) de cada corrida con pesos guardados."""
    runs = []
    for path in glob.glob(os.path.join(RUNS_DIR, "*", "model.zip")):
        tag = os.path.basename(os.path.dirname(path))
        number = _run_number(tag)
        if number is not None:
            runs.append((number, os.path.getmtime(path), tag))
    return runs

def get_latest_version() -> str | None:
    """Tag de la corrida guardada mas reciente (mayor numero; si empatan, la ultima modificada)."""
    runs = _saved_runs()
    return max(runs)[2] if runs else None

def get_author() -> str:
    """Primer nombre del user.name de git, normalizado (Lucio Luque Materazzi -> lucio, teo-mk -> teo)."""
    try:
        name = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        name = ""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    parts = re.split(r"[^a-z0-9]+", name)
    author = next((part for part in parts if part), "")
    if not author:
        print("WARNING: no se pudo leer git config user.name, la corrida queda como autor 'unknown'.")
        return "unknown"
    return author

def get_next_run_id() -> str:
    """v<N>-<autor>, con N mayor a cualquier corrida existente (de cualquier autor).

    Cuenta tambien las corridas que se cortaron antes de guardar pesos, para no reusar su numero.
    """
    tags = os.listdir(RUNS_DIR) if os.path.isdir(RUNS_DIR) else []
    numbers = [n for n in map(_run_number, tags) if n is not None]
    next_number = max(numbers) + 1 if numbers else 0
    return f"v{next_number}-{get_author()}"


def parse_args(eval: bool = False, new_args: list[tuple[str, type, any, str]] | None = None):
    intent = "evaluate" if eval else "train"
    parser = argparse.ArgumentParser(description=f"Do {intent} PPO policy on moving-platform landing.")
    load_help = (
        "Run to load, e.g. v16-lucio, or 15 for old runs (defaults to latest saved run)." if eval
        else "Run to continue training from, e.g. v16-lucio, or 15 for old runs (defaults to new training)."
    )
    parser.add_argument("--load", default=None, help=load_help, type=str)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed.")
    
    if new_args is not None:
        for arg in new_args:
            parser.add_argument(f"--{arg[0]}", type=arg[1], default=arg[2], help=arg[3])

    return parser.parse_args()

def set_global_seeds(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    set_random_seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def get_env_kwargs(gui: bool) -> dict:
    with open("levels.yaml", "r") as f:
        config = yaml.safe_load(f)
    defaults = config["defaults"]
    env_params = config[LEVEL]

    env_kwargs = dict(gui=gui, ctrl_freq=DEFAULT_CTRL_FREQ, max_episode_seconds=DEFAULT_MAX_EPISODE_SECONDS, **defaults)
    env_kwargs.update(env_params)
    return env_kwargs

def make_env(gui: bool, seed: int | None = None):
    def _init():
        env = MovingPlatformLandingAviary(**get_env_kwargs(gui))
        env = Monitor(env)
        if seed is not None:
            env.action_space.seed(seed)
        return env

    return _init