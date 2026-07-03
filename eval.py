import time

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from utils import DEFAULT_CTRL_FREQ, parse_args, get_model_path, get_vecnormalize_path, get_latest_version, make_env, set_global_seeds

DEFAULT_EVAL_EPISODES = 5

def main():
    new_args = [
        ("episodes", int, DEFAULT_EVAL_EPISODES, "Number of evaluation episodes."),
    ]
    args = parse_args(eval=True, new_args=new_args)
    set_global_seeds(args.seed)

    # --load lets you evaluate any saved version; defaults to the latest one.
    version = args.load if args.load is not None else get_latest_version()
    if version is None:
        raise SystemExit("No saved weights found to evaluate. Train a model first.")

    model_path = get_model_path(version, with_extension=True)
    vecnormalize_path = get_vecnormalize_path(version)

    env = DummyVecEnv([make_env(gui=True, seed=args.seed)])
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