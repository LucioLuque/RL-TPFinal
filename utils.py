import argparse
import glob
import random
import re
import torch
import numpy as np
import yaml

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.utils import set_random_seed

from env import MovingPlatformLandingAviary

DEFAULT_CTRL_FREQ = 24
DEFAULT_MAX_EPISODE_SECONDS = 20
DEFAULT_SEED = 42

def get_model_path(version: int, with_extension: bool = False) -> str:
    base = f"weights/ppo_version_{version}"
    if with_extension:
        return f"{base}.zip"
    return base

def get_vecnormalize_path(version: int) -> str:
    return f"vecnorms/vecnormalize_version_{version}.pkl"

def get_latest_version() -> int | None:
    versions = []
    for path in glob.glob(get_model_path("*", with_extension=True)):
        match = re.search(r"ppo_version_(\d+)\.zip$", path)
        if match:
            versions.append(int(match.group(1)))
    return max(versions) if versions else None


def parse_args(eval: bool = False, new_args: list[tuple[str, type, any, str]] | None = None):
    intent = "evaluate" if eval else "train"
    parser = argparse.ArgumentParser(description=f"Do {intent} PPO policy on moving-platform landing.")
    load_help = (
        "Weight/vecnorm version number to load (defaults to latest saved version)." if eval
        else "Weight/vecnorm version number to continue training from (defaults to new training)."
    )
    parser.add_argument("--load", default=None, help=load_help, type=int)
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

def make_env(gui: bool, seed: int | None = None):
    def _init():
        with open("levels.yaml", "r") as f:
            config = yaml.safe_load(f)
        defaults = config["defaults"]
        env_params = config["turtlebot_hard_fixed"]

        env_kwargs = dict(gui=gui, ctrl_freq=DEFAULT_CTRL_FREQ, max_episode_seconds=DEFAULT_MAX_EPISODE_SECONDS, **defaults)
        env_kwargs.update(env_params)

        env = MovingPlatformLandingAviary(**env_kwargs)
        env = Monitor(env)
        if seed is not None:
            env.action_space.seed(seed)
        return env

    return _init