"""PPO con CAPS (Mysore et al. 2021, "Regularizing Action Policies for Smooth Control with Reinforcement Learning").

Suma a la perdida de PPO dos terminos de suavidad sobre la media de la politica:
- temporal: lambda_T * ||mu(s_t) - mu(s_{t+1})||, con pares de pasos consecutivos del mismo episodio;
- espacial: lambda_S * ||mu(s) - mu(s + ruido)||, con ruido gaussiano de desvio sigma en la observacion normalizada.

A diferencia de castigar el cambio de accion en la recompensa (reward_action_coef), no cambia los retornos: no puede
dejar al dron flotando (BITACORA.md, "trampa de flotar"). Ver docs/estado-del-arte-2026-10-30.md.

train() es el de PPO de stable-baselines3 2.9.0 con el bloque marcado "CAPS". El modelo guardado se carga con
PPO.load (CAPS solo cambia el entrenamiento); para seguir entrenando con CAPS hay que cargarlo con CAPSPPO.load.
"""
import numpy as np
import torch as th
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.utils import explained_variance
from torch.nn import functional as F


class CAPSPPO(PPO):
    def __init__(self, *args, caps_temporal: float = 0.0, caps_spatial: float = 0.0, caps_sigma: float = 0.02, **kwargs):
        self.caps_temporal = caps_temporal
        self.caps_spatial = caps_spatial
        self.caps_sigma = caps_sigma
        super().__init__(*args, **kwargs)

    def _mean_action(self, obs: th.Tensor) -> th.Tensor:
        return self.policy.get_distribution(obs).distribution.mean

    def _consecutive_pairs(self) -> tuple[th.Tensor, th.Tensor]:
        """(s_t, s_{t+1}) del rollout, sin los pares que cruzan el fin de un episodio."""
        obs = self.rollout_buffer.observations           # (n_steps, n_envs, obs_dim), antes de que get() lo aplane
        starts = self.rollout_buffer.episode_starts      # (n_steps, n_envs): 1 si el paso empieza un episodio
        valid = starts[1:] == 0
        return (th.as_tensor(obs[:-1][valid], device=self.device), th.as_tensor(obs[1:][valid], device=self.device))

    def train(self) -> None:
        self.policy.set_training_mode(True)
        self._update_learning_rate(self.policy.optimizer)
        clip_range = self.clip_range(self._current_progress_remaining)  # type: ignore[operator]
        if self.clip_range_vf is not None:
            clip_range_vf = self.clip_range_vf(self._current_progress_remaining)  # type: ignore[operator]

        entropy_losses = []
        pg_losses, value_losses = [], []
        clip_fractions = []
        caps_t_losses, caps_s_losses = [], []
        obs_t, obs_t1 = self._consecutive_pairs()

        continue_training = True
        for epoch in range(self.n_epochs):
            approx_kl_divs = []
            for rollout_data in self.rollout_buffer.get(self.batch_size):
                actions = rollout_data.actions
                if isinstance(self.action_space, spaces.Discrete):
                    actions = rollout_data.actions.long().flatten()

                values, log_prob, entropy = self.policy.evaluate_actions(rollout_data.observations, actions)
                values = values.flatten()
                advantages = rollout_data.advantages
                if self.normalize_advantage and len(advantages) > 1:
                    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

                ratio = th.exp(log_prob - rollout_data.old_log_prob)
                policy_loss_1 = advantages * ratio
                policy_loss_2 = advantages * th.clamp(ratio, 1 - clip_range, 1 + clip_range)
                policy_loss = -th.min(policy_loss_1, policy_loss_2).mean()

                pg_losses.append(policy_loss.item())
                clip_fraction = th.mean((th.abs(ratio - 1) > clip_range).float()).item()
                clip_fractions.append(clip_fraction)

                if self.clip_range_vf is None:
                    values_pred = values
                else:
                    values_pred = rollout_data.old_values + th.clamp(
                        values - rollout_data.old_values, -clip_range_vf, clip_range_vf
                    )
                value_loss = F.mse_loss(rollout_data.returns, values_pred)
                value_losses.append(value_loss.item())

                if entropy is None:
                    entropy_loss = -th.mean(-log_prob)
                else:
                    entropy_loss = -th.mean(entropy)
                entropy_losses.append(entropy_loss.item())

                loss = policy_loss + self.ent_coef * entropy_loss + self.vf_coef * value_loss

                # ---- CAPS ----
                if self.caps_temporal and len(obs_t) > 0:
                    idx = th.randint(len(obs_t), (len(rollout_data.observations),), device=self.device)
                    caps_t = th.norm(self._mean_action(obs_t[idx]) - self._mean_action(obs_t1[idx]), dim=1).mean()
                    loss = loss + self.caps_temporal * caps_t
                    caps_t_losses.append(caps_t.item())
                if self.caps_spatial:
                    obs = rollout_data.observations
                    noisy = th.clamp(obs + self.caps_sigma * th.randn_like(obs), -1.0, 1.0)
                    caps_s = th.norm(self._mean_action(obs) - self._mean_action(noisy), dim=1).mean()
                    loss = loss + self.caps_spatial * caps_s
                    caps_s_losses.append(caps_s.item())
                # ---- fin CAPS ----

                with th.no_grad():
                    log_ratio = log_prob - rollout_data.old_log_prob
                    approx_kl_div = th.mean((th.exp(log_ratio) - 1) - log_ratio).cpu().numpy()
                    approx_kl_divs.append(approx_kl_div)

                if self.target_kl is not None and approx_kl_div > 1.5 * self.target_kl:
                    continue_training = False
                    if self.verbose >= 1:
                        print(f"Early stopping at step {epoch} due to reaching max kl: {approx_kl_div:.2f}")
                    break

                self.policy.optimizer.zero_grad()
                loss.backward()
                th.nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)
                self.policy.optimizer.step()

            self._n_updates += 1
            if not continue_training:
                break

        explained_var = explained_variance(self.rollout_buffer.values.flatten(), self.rollout_buffer.returns.flatten())

        self.logger.record("train/entropy_loss", np.mean(entropy_losses))
        self.logger.record("train/policy_gradient_loss", np.mean(pg_losses))
        self.logger.record("train/value_loss", np.mean(value_losses))
        self.logger.record("train/approx_kl", np.mean(approx_kl_divs))
        self.logger.record("train/clip_fraction", np.mean(clip_fractions))
        self.logger.record("train/loss", loss.item())
        self.logger.record("train/explained_variance", explained_var)
        if caps_t_losses:
            self.logger.record("train/caps_temporal", np.mean(caps_t_losses))
        if caps_s_losses:
            self.logger.record("train/caps_spatial", np.mean(caps_s_losses))
        if hasattr(self.policy, "log_std"):
            self.logger.record("train/std", th.exp(self.policy.log_std).mean().item())

        self.logger.record("train/n_updates", self._n_updates, exclude="tensorboard")
        self.logger.record("train/clip_range", clip_range)
        if self.clip_range_vf is not None:
            self.logger.record("train/clip_range_vf", clip_range_vf)
