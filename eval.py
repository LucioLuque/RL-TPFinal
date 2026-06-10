import time

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from utils import DEFAULT_CTRL_FREQ, parse_args, get_model_path, get_vecnormalize_path, make_env, set_global_seeds

def main():
    new_args = [ # Add argument option to use specific level weights and vecnorms to cross-evaluate on another level
        ("episodes", int, 5, "Number of evaluation episodes."),
        ("weights", int, None, "Level of the weights and vecnorms to use for evaluation (defaults to the evaluation level)."),
    ]
    args = parse_args(eval=True, new_args=new_args)
    set_global_seeds(args.seed)

    level_load = args.weights if args.weights is not None else args.level

    model_path = get_model_path(level_load, with_extension=True)
    vecnormalize_path = get_vecnormalize_path(level_load)

    env = DummyVecEnv([make_env(args.level, gui=True, seed=args.seed)])
    env = VecNormalize.load(vecnormalize_path, env)

    env.training = False
    env.norm_reward = False

    model = PPO.load(model_path, env=env, device="cpu")

    obs = env.reset()
    successful_landings = 0

    for episode in range(args.episodes):
        while True:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)

            time.sleep(1 / DEFAULT_CTRL_FREQ)

            if done:
                print(f"Episodio {episode + 1} terminado")
                print("Info:", info)
                if info[0].get("is_success", False):
                    successful_landings += 1
                obs = env.reset()
                break

    print(f"Éxitos: {successful_landings}/{args.episodes}")
    env.close()


if __name__ == "__main__":
    main()