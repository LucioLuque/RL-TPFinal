import glob
import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

# Mapeo de tags
TAG_LABELS: Dict[str, str] = {
    "rollout/ep_len_mean": "Duración media del episodio",
    "rollout/ep_rew_mean": "Recompensa media por episodio",
    "rollout/success_rate": "Tasa de éxito",
    "time/fps": "FPS",
    "train/approx_kl": "Divergencia KL aproximada",
    "train/clip_fraction": "Fracción de clipping",
    "train/clip_range": "Rango de clipping",
    "train/entropy_loss": "Pérdida de entropía",
    "train/explained_variance": "Varianza explicada",
    "train/learning_rate": "Tasa de aprendizaje",
    "train/loss": "Pérdida total",
    "train/policy_gradient_loss": "Pérdida de gradiente de política",
    "train/std": "Desviación estándar de la acción",
    "train/value_loss": "Pérdida de valor",
}

def _label_for(tag: str) -> str:
    return TAG_LABELS.get(tag, tag)

def _load_scalars(version: int, path_template: str = "logs/version_{v}/PPO_1") -> Dict[str, List[Tuple[int, float]]]:
    log_dir = path_template.format(v=version)
    event_files = sorted(glob.glob(os.path.join(log_dir, "events.out.tfevents.*")))
    if not event_files:
        raise FileNotFoundError(f"No se encontraron event files en '{log_dir}'.")

    ea = EventAccumulator(log_dir, size_guidance={"scalars": 0})
    ea.Reload()

    tags = ea.Tags().get("scalars", [])
    data = {}
    for tag in tags:
        events = ea.Scalars(tag)
        data[tag] = [(e.step, e.value) for e in events]
    return data

def list_available_tags(version: int, path_template: str = "logs/version_{v}/PPO_1") -> List[str]:
    data = _load_scalars(version, path_template)
    return sorted(data.keys())

def _versions_suffix(versions: Dict[int, str]) -> str:
    return "v" + "_".join(str(v) for v in sorted(versions.keys()))

def _normalize_vlines(vlines) -> Dict[float, str]:
    if vlines is None:
        return {}
    if isinstance(vlines, dict):
        return vlines
    return {step: "" for step in vlines}

def _filter_by_max_steps(data: List[Tuple[int, float]], max_steps: int | None) -> List[Tuple[int, float]]:
    if max_steps is None:
        return data

    return [(step, value) for step, value in data if step <= max_steps]

def _smooth_values(values: List[float], smooth: float | None) -> List[float]:
    if smooth is None or smooth <= 0:
        return values

    if not 0 <= smooth < 1:
        raise ValueError("El parámetro smooth debe estar en el rango [0, 1).")

    smoothed = []
    last = values[0]

    for value in values:
        last = last * smooth + value * (1 - smooth)
        smoothed.append(last)

    return smoothed

def plot_tensorboard_metrics(versions: Dict[int, str], tags: List[str], path_template: str = "logs/version_{v}/PPO_1", figsize: Tuple[int, int] | None = None, save_dir: str | None = None, show: bool = True, vlines=None, max_steps: int | None = None, smooth: float | None = None):
    all_data = {v: _load_scalars(v, path_template) for v in versions}
    versions_suffix = _versions_suffix(versions)
    folder = "landing_level_1" if "landing_level_1" in path_template else "version_logs"
    vlines = _normalize_vlines(vlines)

    n_tags = len(tags)
    if figsize is None:
        figsize = (12, 3 * n_tags)

    fig, axes = plt.subplots(n_tags, 1, figsize=figsize, squeeze=False, sharex=True)

    for ax, tag in zip(axes[:, 0], tags):
        for version, label in versions.items():
            data = all_data[version].get(tag)
            if not data:
                print(f"Tag '{tag}' no encontrado en {path_template.format(v=version)}.")
                continue

            data = _filter_by_max_steps(data, max_steps)

            steps, values = zip(*data)

            values = list(values)

            if smooth is not None and smooth > 0:
                not_smooth, = ax.plot(steps, values, alpha=0.25, linewidth=1, label=None)
                color = not_smooth.get_color()
                smooth_values = _smooth_values(values, smooth)
                ax.plot(steps, smooth_values, linewidth=2, label=label, color=color)
            else:
                ax.plot(steps, values, linewidth=2, label=label)

        for step, vlabel in vlines.items():
            ax.axvline(x=step, color="red", linestyle="--", label=vlabel if vlabel else None, alpha=0.4)

        if ax == axes[-1, 0]:
            ax.set_xlabel("Timestep")
        else:
            ax.set_xlabel("")
            # ax.set_xticklabels([])
        ax.set_ylabel(_label_for(tag))
        ax.legend()
        ax.grid(alpha=0.3)

    plt.tight_layout()

    if save_dir is not None:
        os.makedirs(save_dir, exist_ok=True)
        safe_tags = "_".join(tag.replace("/", "_") for tag in tags)
        filename = f"{folder}_{safe_tags}_{versions_suffix}.png"
        plt.savefig(os.path.join(save_dir, filename), dpi=150)

    if show:
        plt.show()
    else:
        plt.close()

    return all_data




if __name__ == "__main__":

    print(list_available_tags(version=0))

    # #plot 1
    # a)
    # plot_tensorboard_metrics(
    #     versions={
    #         4: "",
    #         # 3: "Curriculum + reward shaping",
    #     },
    #     tags=[
    #         "rollout/success_rate",
    #         # "train/approx_kl",
    #     ],
    #     path_template="logs/landing_level_1/PPO_{v}",
    #     save_dir="plots",
    #     show=True,
    #     figsize=(8, 4),
    #     # vlines={2373000: "Cambio de curriculum"},
    # )

    # b)
    # plot_tensorboard_metrics(
    #     versions={
    #         4: "",
    #         # 3: "Curriculum + reward shaping",
    #     },
    #     tags=[
    #         # "rollout/success_rate",
    #         "train/approx_kl",
    #     ],
    #     path_template="logs/landing_level_1/PPO_{v}",
    #     save_dir="plots",
    #     show=True,
    #     figsize=(8, 4),
    #     # vlines={2373000: "Cambio de curriculum"},
    # )

    # # plot 3
    # plot_tensorboard_metrics(
    #     versions={
    #         2: r"$k_{ang} = 0.001$",
    #         3: r"$k_{ang} = 0.01$"
    #     },
    #     tags=[
    #         "rollout/success_rate",
    #         # "train/explained_variance",
    #         # "rollout/ep_rew_mean"

    #     ],
    #     # path_template="logs/landing_level_1/PPO_{v}",
    #     path_template="logs/version_{v}/PPO_1",
    #     save_dir="plots",
    #     show=True,
    #     max_steps=6000000,
    #     smooth = 0.9,
    #     figsize=(8, 4),
    #     # vlines={2166000: ""},
    # )

    # plot 4
    # plot_tensorboard_metrics(
    #     versions={
    #         2: r"Distancia",
    #         4: r"Progreso",
    #         6: r"Progreso y distancia"
    #     },
    #     tags=[
    #         "rollout/success_rate",
    #         # "train/explained_variance",
    #         # 'rollout/ep_len_mean'

    #     ],
    #     # path_template="logs/landing_level_1/PPO_{v}",
    #     path_template="logs/version_{v}/PPO_1",
    #     save_dir="plots",
    #     show=True,
    #     max_steps=6000000,
    #     smooth = 0.9,
    #     figsize=(8, 4),
    #     # vlines={2166000: ""},
    # # )

    # # plot 5
    # plot_tensorboard_metrics(
    #     versions={
    #         7: r"$k_{t} = 0.2$",
    #         8: r"$k_{t} = 0.1$",
    #     },
    #     tags=[
    #         "rollout/success_rate",
    #         # "train/explained_variance",
    #         # "rollout/ep_rew_mean"

    #     ],
    #     # path_template="logs/landing_level_1/PPO_{v}",
    #     path_template="logs/version_{v}/PPO_1",
    #     save_dir="plots",
    #     show=True,
    #     max_steps=4500000,
    #     smooth = 0.4,
    #     figsize=(8, 4),
    #     # vlines={2166000: ""},
    # )

    # plot 6
    plot_tensorboard_metrics(
        versions={
            1: r"V1",
            # 2: r"V2",
            # 3: r"V3",
            8: r"$K_t = 0.1$",
            13: r"Velocity tracking",

        },
        tags=[
            "rollout/success_rate",
            # "train/explained_variance",
            # "rollout/ep_rew_mean"
            # "rollout/ep_len_mean"

        ],
        # path_template="logs/landing_level_1/PPO_{v}",
        path_template="logs/version_{v}/PPO_1",
        save_dir="plots",
        show=True,
        max_steps=4500000,
        smooth = 0.9,
        figsize=(8, 4),
        # vlines={2166000: ""},
    )