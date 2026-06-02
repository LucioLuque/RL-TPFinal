import argparse
import random
import torch
import numpy as np

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.utils import set_random_seed


from platform1 import MovingPlatformLandingAviary


MODE_CHOICES = ("static", "linear", "turtlebot")
DEFAULT_CTRL_FREQ = 24
DEFAULT_MAX_EPISODE_SECONDS = 20
DEFAULT_PLATFORM_RADIUS = 0.2
DEFAULT_SEED = 42


def get_model_path(mode: str, with_extension: bool = False) -> str:
    base = f"ppo_landing_{mode}_platform"
    if with_extension:
        return f"{base}.zip"
    return base


def get_vecnormalize_path(mode: str) -> str:
    return f"vecnormalize_landing_{mode}.pkl"


def parse_args(eval: bool = False, new_arg: tuple | None = None):
    intent = "evaluate" if eval else "train"
    parser = argparse.ArgumentParser(description=f"Do {intent} a PPO policy on the moving-platform landing task.")
    parser.add_argument(
        "--mode",
        choices=MODE_CHOICES,
        default="static",
        help=f"Platform movement mode to {intent}.",
    )
    if new_arg is not None:
        parser.add_argument(
            f"--{new_arg[0]}",
            type=new_arg[1],
            default=new_arg[2],
            help=new_arg[3],
        )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random seed for training and evaluation.",
    )
    return parser.parse_args()


def set_global_seeds(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    set_random_seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def make_env(mode: str, gui: bool, seed: int | None = None):
    def _init():
        env_kwargs = dict(
            mode=mode,
            gui=gui,
            ctrl_freq=DEFAULT_CTRL_FREQ,
            max_episode_seconds=DEFAULT_MAX_EPISODE_SECONDS,
            platform_radius=DEFAULT_PLATFORM_RADIUS,
        )

        if mode == "linear":
            env_kwargs["linear_speed_range"] = (0.1, 0.4)
        elif mode == "turtlebot":
            env_kwargs["turtle_linear_speed_range"] = (0.1, 0.3)
            env_kwargs["turtle_angular_speed_range"] = (0.1, 0.8)

        env = MovingPlatformLandingAviary(**env_kwargs)
        env = Monitor(env)
        if seed is not None:
            env.reset(seed=seed)
            env.action_space.seed(seed)
        return env

    return _init
