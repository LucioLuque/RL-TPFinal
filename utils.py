import argparse
import random
import torch
import numpy as np
import yaml

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.utils import set_random_seed


from platform1 import MovingPlatformLandingAviary

# MODE_CHOICES = ("static", "linear", "turtlebot")
LEVEL_CHOICES = tuple(range(0, 6))
DEFAULT_CTRL_FREQ = 24
DEFAULT_MAX_EPISODE_SECONDS = 20
DEFAULT_SEED = 42

def get_model_path(level: int, with_extension: bool = False) -> str:
    base = f"weights/ppo_landing_level_{level}"
    if with_extension:
        return f"{base}.zip"
    return base


def get_vecnormalize_path(level: int) -> str:
    return f"vecnorms/vecnormalize_landing_level_{level}.pkl"


def parse_args(eval: bool = False, new_args: list[tuple[str, type, any, str]] | None = None):
    intent = "evaluate" if eval else "train"
    parser = argparse.ArgumentParser(description=f"Do {intent} a PPO policy on the moving-platform landing task.")
    parser.add_argument(
        "--level",
        choices=LEVEL_CHOICES,
        default=1,
        help=f"Level to {intent}.",
        type=int,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random seed for training and evaluation.",
    )
    if new_args is not None:
        for arg in new_args:
            parser.add_argument(
                f"--{arg[0]}",
                type=arg[1],
                default=arg[2],
                help=arg[3],
        )

    return parser.parse_args()


def set_global_seeds(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    set_random_seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def make_env(level: int, gui: bool, seed: int | None = None):
    def _init():
        with open("levels.yaml", "r") as f:
            config = yaml.safe_load(f)
        defaults = config["defaults"]
        level_params = config["levels"][level]
        level_params.pop("id") 

        env_kwargs = dict(
            gui=gui,
            ctrl_freq=DEFAULT_CTRL_FREQ,
            max_episode_seconds=DEFAULT_MAX_EPISODE_SECONDS,
            **defaults,
        )
        env_kwargs.update(level_params)

        env = MovingPlatformLandingAviary(**env_kwargs)
        env = Monitor(env)
        if seed is not None:
            env.reset(seed=seed)
            env.action_space.seed(seed)
        return env

    return _init
