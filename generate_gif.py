import time
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
import pybullet as p

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from utils import (
    DEFAULT_CTRL_FREQ,
    parse_args,
    get_model_path,
    get_vecnormalize_path,
    get_latest_version,
    make_env,
    set_global_seeds,
)


DEFAULT_GIF_FPS = 12
DEFAULT_CAPTURE_EVERY = 2
DEFAULT_IMAGE_WIDTH = 640
DEFAULT_IMAGE_HEIGHT = 480
DEFAULT_OUT_DIR = "outputs"


def unwrap_env(env):
    """
    Recupera el MovingPlatformLandingAviary real desde wrappers tipo Monitor.
    """
    while hasattr(env, "env"):
        env = env.env

    return env


def get_drone_id(env):
    if hasattr(env, "DRONE_IDS"):
        return env.DRONE_IDS[0]

    raise AttributeError(
        "No encontré env.DRONE_IDS. Revisá cómo se llama el id del dron "
        "en MovingPlatformLandingAviary."
    )


def get_current_drone_pose(env):
    drone_id = get_drone_id(env)

    pos, quat = p.getBasePositionAndOrientation(
        drone_id,
        physicsClientId=env.CLIENT,
    )

    return np.array(pos, dtype=np.float32), np.array(quat, dtype=np.float32)


def capture_frame(
    env,
    width: int = DEFAULT_IMAGE_WIDTH,
    height: int = DEFAULT_IMAGE_HEIGHT,
    camera_distance: float = 1.5,
    camera_yaw: float = 45.0,
    camera_pitch: float = -30.0,
):
    """
    Captura un frame RGB desde PyBullet.

    La cámara apunta a un punto intermedio entre el dron y la plataforma.
    """
    drone_pos, _ = get_current_drone_pose(env)
    platform_pos = np.array(env.platform_pos, dtype=np.float32)

    target = 0.5 * drone_pos + 0.5 * platform_pos
    target[2] = max(0.5, target[2])

    view_matrix = p.computeViewMatrixFromYawPitchRoll(
        cameraTargetPosition=target.tolist(),
        distance=camera_distance,
        yaw=camera_yaw,
        pitch=camera_pitch,
        roll=0.0,
        upAxisIndex=2,
    )

    projection_matrix = p.computeProjectionMatrixFOV(
        fov=60.0,
        aspect=width / height,
        nearVal=0.1,
        farVal=100.0,
    )

    _, _, rgba, _, _ = p.getCameraImage(
        width=width,
        height=height,
        viewMatrix=view_matrix,
        projectionMatrix=projection_matrix,
        renderer=p.ER_BULLET_HARDWARE_OPENGL,
        physicsClientId=env.CLIENT,
    )

    rgba = np.reshape(rgba, (height, width, 4))
    rgb = rgba[:, :, :3].astype(np.uint8)

    return rgb


def normalize_obs(vecnormalize_env, obs):
    """
    Normaliza una observación individual usando las estadísticas de VecNormalize.

    El modelo fue entrenado con VecNormalize, entonces para hacer predict
    correctamente necesitamos pasarle la observación normalizada.
    """
    obs_batch = np.array([obs], dtype=np.float32)
    return vecnormalize_env.normalize_obs(obs_batch)


def main():
    # Ejemplos:
    # python view_platform.py
    # python view_platform.py --load 4
    # python view_platform.py --load 4 --image-width 480 --image-height 360

    new_args = [
        ("gif-fps", int, DEFAULT_GIF_FPS, "FPS of the output GIF."),
        ("capture-every", int, DEFAULT_CAPTURE_EVERY, "Capture one frame every N env steps."),
        ("image-width", int, DEFAULT_IMAGE_WIDTH, "GIF width."),
        ("image-height", int, DEFAULT_IMAGE_HEIGHT, "GIF height."),
        ("out-dir", str, DEFAULT_OUT_DIR, "Directory where the GIF will be saved."),
        ("no-sleep", bool, False, "Run without real-time sleep."),
    ]

    args = parse_args(eval=True, new_args=new_args)
    set_global_seeds(args.seed)

    version = args.load if args.load is not None else get_latest_version()

    model_path = get_model_path(version, with_extension=True)
    vecnormalize_path = get_vecnormalize_path(version)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    gif_path = out_dir / f"policy_version_{version}_episode.gif"

    print("── view one policy episode ──")
    print(f"version: {version}")
    print(f"model_path: {model_path}")
    print(f"vecnormalize_path: {vecnormalize_path}")
    print(f"ctrl_freq: {DEFAULT_CTRL_FREQ}")
    print(f"gif_path: {gif_path}")

    # ------------------------------------------------------------------
    # 1. Cargamos VecNormalize y PPO como en eval.py.
    #    Este env se usa para tener estadísticas de normalización.
    # ------------------------------------------------------------------
    norm_env = DummyVecEnv([make_env(gui=False, seed=args.seed)])
    norm_env = VecNormalize.load(vecnormalize_path, norm_env)

    norm_env.training = False
    norm_env.norm_reward = False

    model = PPO.load(
        model_path,
        env=norm_env,
        device="cpu",
    )

    # ------------------------------------------------------------------
    # 2. Creamos un entorno real con GUI.
    #    Este lo pisamos manualmente para evitar el autoreset de DummyVecEnv.
    # ------------------------------------------------------------------
    env = make_env(gui=True, seed=args.seed)()
    obs, info = env.reset(seed=args.seed)

    raw_env = unwrap_env(env)

    obs_norm = normalize_obs(norm_env, obs)

    gif_frames = []

    successful_landing = False
    crashed = False
    truncated = False

    step = 0

    while True:
        if step % args.capture_every == 0:
            frame = capture_frame(
                raw_env,
                width=args.image_width,
                height=args.image_height,
            )
            gif_frames.append(frame)

        action, _ = model.predict(obs_norm, deterministic=True)

        action_for_env = action[0] if action.ndim == 2 else action

        obs, reward, terminated, is_truncated, info = env.step(action_for_env)

        done = terminated or is_truncated

        if step % DEFAULT_CTRL_FREQ == 0:
            drone_pos, _ = get_current_drone_pose(raw_env)

            print(
                f"t: {round(step / DEFAULT_CTRL_FREQ, 2)}s",
                f"| drone_pos: {np.round(drone_pos, 3)}",
                f"| platform_pos: {np.round(raw_env.platform_pos, 3)}",
                f"| platform_vel: {np.round(raw_env.platform_vel, 3)}",
                f"| reward: {round(float(reward), 3)}",
            )

        if done:
            # Capturamos un último frame del estado terminal.
            frame = capture_frame(
                raw_env,
                width=args.image_width,
                height=args.image_height,
            )
            gif_frames.append(frame)

            successful_landing = info.get("is_success", False)
            crashed = info.get("crashed", False)
            truncated = bool(is_truncated)

            print("── episode done ──")
            print("Info:", info)
            break

        obs_norm = normalize_obs(norm_env, obs)

        if not args.no_sleep:
            time.sleep(1 / DEFAULT_CTRL_FREQ)

        step += 1

    if len(gif_frames) > 0:
        imageio.mimsave(
            gif_path,
            gif_frames,
            fps=args.gif_fps,
        )

        print(f"GIF guardado en: {gif_path}")
    else:
        print("No se capturaron frames. No se generó GIF.")

    print("── resumen ──")
    print(f"steps: {step + 1}")
    print(f"time: {round((step + 1) / DEFAULT_CTRL_FREQ, 2)}s")
    print(f"success: {successful_landing}")
    print(f"crashed: {crashed}")
    print(f"truncated: {truncated}")

    env.close()
    norm_env.close()


if __name__ == "__main__":
    main()