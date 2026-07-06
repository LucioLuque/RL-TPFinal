# from __future__ import annotations

# from typing import Callable, Iterable

# import matplotlib.pyplot as plt
# from tensorboard.backend.event_processing import event_accumulator


LOG_DIR = "../logs"

# # Edit these values by hand before running the script.
# VERSIONS = [1]
# METRICS = [
# 	"rollout/ep_rew_mean",
# 	"rollout/ep_len_mean",
# 	"rollout/success_rate",
# 	"train/loss",
# ]
# SMOOTH_WINDOW = 1
# SAVE_PATH = None  # Example: Path("plots/output/reward_curves.png")
# SHOW_PLOT = True


# DEFAULT_METRICS = [
# 	"rollout/ep_rew_mean",
# 	"rollout/ep_len_mean",
# 	"rollout/success_rate",
# 	"train/loss",
# ]

# StyleFn = Callable[[plt.Axes, str], None]


# def load_scalar_series(log_dir: Path, metric: str):
# 	accumulator = event_accumulator.EventAccumulator(str(log_dir), size_guidance={"scalars": 0})
# 	accumulator.Reload()

# 	available = accumulator.Tags().get("scalars", [])
# 	if metric not in available:
# 		raise KeyError(
# 			f"Metric '{metric}' not found in {log_dir}. Available scalars: {', '.join(sorted(available)) or 'none'}"
# 		)

# 	events = accumulator.Scalars(metric)
# 	steps = [event.step for event in events]
# 	values = [event.value for event in events]
# 	return steps, values


# def fetch_metric_series(
# 	versions: list[int],
# 	metrics: list[str],
# 	logs_root: Path = LOGS_ROOT,
# ) -> dict[int, dict[str, tuple[list[int], list[float]]]]:
# 	series_by_version: dict[int, dict[str, tuple[list[int], list[float]]]] = {}

# 	for version in versions:
# 		log_dir = find_event_dir(version, logs_root=logs_root)
# 		if not log_dir.exists():
# 			print(f"Skipping version {version}: {log_dir} does not exist")
# 			continue

# 		version_series: dict[str, tuple[list[int], list[float]]] = {}
# 		for metric in metrics:
# 			try:
# 				steps, values = load_scalar_series(log_dir, metric)
# 			except KeyError as exc:
# 				print(exc)
# 				continue

# 			if not steps:
# 				print(f"Skipping version {version}: metric '{metric}' has no points")
# 				continue

# 			version_series[metric] = (steps, values)

# 		if version_series:
# 			series_by_version[version] = version_series

# 	return series_by_version


# def smooth(values: Iterable[float], window: int) -> list[float]:
# 	values = list(values)
# 	if window <= 1 or len(values) < window:
# 		return values

# 	smoothed = []
# 	running_sum = 0.0
# 	for index, value in enumerate(values):
# 		running_sum += value
# 		if index >= window:
# 			running_sum -= values[index - window]
# 		smoothed.append(running_sum / min(window, index + 1))
# 	return smoothed


# def apply_axis_style(axis: plt.Axes, metric: str) -> None:
# 	axis.set_title(metric)
# 	axis.set_xlabel("step")
# 	axis.set_ylabel(metric)
# 	axis.grid(True, alpha=0.3)


# def apply_reward_style(axis: plt.Axes, metric: str) -> None:
# 	apply_axis_style(axis, metric)
# 	axis.axhline(0.0, color="black", linewidth=0.8, alpha=0.2)


# def apply_loss_style(axis: plt.Axes, metric: str) -> None:
# 	apply_axis_style(axis, metric)
# 	axis.set_yscale("log")


# def main_plotting_function(
# 	versions: list[int],
# 	metrics: list[str],
# 	smooth_window: int = 1,
# 	style_fn: StyleFn | None = None,
# 	title: str | None = None,
# 	save_path: Path | None = None,
# 	show: bool = True,
# 	logs_root: Path = LOGS_ROOT,
# ) -> None:
# 	series_by_version = fetch_metric_series(versions, metrics, logs_root=logs_root)
# 	fig, axes = plt.subplots(len(metrics), 1, sharex=False, figsize=(11, 4 * len(metrics)))
# 	if len(metrics) == 1:
# 		axes = [axes]

# 	for axis, metric in zip(axes, metrics):
# 		plotted_anything = False

# 		for version in versions:
# 			version_series = series_by_version.get(version)
# 			if version_series is None or metric not in version_series:
# 				continue

# 			steps, values = version_series[metric]
# 			values = smooth(values, smooth_window)
# 			axis.plot(steps, values, label=f"version {version}")
# 			plotted_anything = True

# 		if style_fn is not None:
# 			style_fn(axis, metric)
# 		else:
# 			apply_axis_style(axis, metric)

# 		if plotted_anything:
# 			axis.legend()

# 	if title is not None:
# 		fig.suptitle(title)
# 		fig.tight_layout(rect=(0, 0, 1, 0.97))
# 	else:
# 		fig.tight_layout()

# 	if save_path is not None:
# 		save_path.parent.mkdir(parents=True, exist_ok=True)
# 		fig.savefig(save_path, dpi=150, bbox_inches="tight")
# 		print(f"Saved plot to {save_path}")

# 	if show and plt.get_backend().lower() != "agg":
# 		plt.show()
# 	else:
# 		plt.close(fig)


# def plot_default() -> None:
# 	main_plotting_function(
# 		versions=VERSIONS,
# 		metrics=METRICS,
# 		smooth_window=SMOOTH_WINDOW,
# 		style_fn=apply_axis_style,
# 		save_path=SAVE_PATH,
# 		show=SHOW_PLOT,
# 	)


# def plot_training_summary() -> None:
# 	main_plotting_function(
# 		versions=VERSIONS,
# 		metrics=["rollout/ep_rew_mean", "rollout/ep_len_mean", "rollout/success_rate"],
# 		smooth_window=SMOOTH_WINDOW,
# 		style_fn=apply_reward_style,
# 		save_path=SAVE_PATH,
# 		show=SHOW_PLOT,
# 	)


# def plot_optimization_curves() -> None:
# 	main_plotting_function(
# 		versions=VERSIONS,
# 		metrics=["train/loss", "train/value_loss", "train/policy_gradient_loss"],
# 		smooth_window=SMOOTH_WINDOW,
# 		style_fn=apply_loss_style,
# 		save_path=SAVE_PATH,
# 		show=SHOW_PLOT,
# 	)

def fetch(versions, metrics):
	series_by_version: dict[int, dict[str, tuple[list[int], list[float]]]] = {}

	for version in versions:
		dir = f"{LOG_DIR}/version_{version}/PPO_1"	
		version_metrics = {}

		for metric in metrics:
			accumulator = event_accumulator.EventAccumulator(str(dir), size_guidance={"scalars": 0})
			accumulator.Reload()

			events = accumulator.Scalars(metric)
			steps = [event.step for event in events]
			values = [event.value for event in events]
			version_metrics[metric] = (steps, values)

		series_by_version[version] = version_metrics
	
	return series_by_version