# para level 0 (0.13 cte). Entrenado 1M 8 envs, data 38 creo
def _computeReward(self):
        state = self._getDroneStateVector(0)
        drone_pos = state[0:3]
        drone_vel = state[10:13]

        rel_pos = drone_pos - self.platform_pos
        rel_vel = drone_vel - self.platform_vel

        d_xy    = np.linalg.norm(rel_pos[0:2])
        d_z     = abs(rel_pos[2])
        v_xy    = np.linalg.norm(rel_vel[0:2])

        reward = 0.0

        reward += 0.2 * v_xy # Si pongo todo v, el dron no baja
        reward -= 0.1 * d_z # Termino para bajar
        reward -= 0.2 * d_xy # Más peso para incentivar aterrizajes centrados

        # --- Terminal ---
        if self.has_landed:
            reward += 25 - d_xy * 10.0 # recompensa mayor cuanto más centrado aterrice
        elif self.has_crashed:
            reward -= 10.0
        elif self.is_truncated:
            reward -= 2.0

        return float(reward)