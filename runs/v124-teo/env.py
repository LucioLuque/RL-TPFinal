import numpy as np
import pybullet as p
from gymnasium import spaces

from gym_pybullet_drones.envs.VelocityAviary import VelocityAviary
from gym_pybullet_drones.utils.enums import DroneModel, Physics

# Velocidad maxima que se le pide al dron (m/s): accion = SPEED_LIMIT * s * direccion.
# VelocityAviary trae 0.25 m/s (3% de 30 km/h), menos que la plataforma (hasta 0.3 m/s), y el dron
# no podia alcanzarla. Tiene que ser el mismo limite que se use en el Crazyflie real (ver SIM2REAL.md en ~/Documents/Tesis/Laboratorio).
DRONE_SPEED_LIMIT = 0.6

# Escalas para normalizar la observacion a [-1, 1] (ver TODO.md, punto 1).
OBS_POS_SCALE = 1.5       # m: el dron aparece a <= 0.8 m en xy y <= 1.5 m de altura; Medir en optitrack real
OBS_ANGLE_SCALE = 0.7     # rad: roll/pitch mayor a esto ya es choque (_crashed)
OBS_ANG_VEL_SCALE = 5.0   # rad/s: sin limite conocido, elegido mirando datos (sigma ~1.2 en v10) Se puede elgir algo mejor que esto?
VEL_MARGIN = 1.25         # margen sobre los limites de velocidad (sobrepaso del controlador, caidas)

class MovingPlatformLandingAviary(VelocityAviary):
    def __init__(
        self,
        gui: bool = False,
        ctrl_freq: int = 48,
        max_episode_seconds: int = 8,
        
        # Plataforma
        linear_speed_range: tuple = (0.1, 0.1), # m/s (min, max)
        angular_speed_range: tuple = (0.0, 0.0), # rad/s (min, max)
        vary_speed: bool = False, # cambiar velocidad de la plataforma durante el episodio
        turt_noise: bool = False, # agregar ruido a la velocidad de la plataforma en cada step
    
        # dron 
        spawn_xy_radius: float = 2,  # radio máximo en XY (m)
        spawn_z_range: tuple = (0.5, 1.5), # altura inicial (m)

        # Recompensa (variantes con nombre en rewards.yaml)
        reward_distance_coef: float = 0.1,  # castigo por paso proporcional a la distancia al tope
        reward_dxy_coef: float = 0.0,       # castigo por paso proporcional a la distancia horizontal
        reward_dz_coef: float = 0.0,        # castigo por paso proporcional a la altura sobre el tope (|dz|)
        reward_progress_coef: float = 0.0,  # premio por acercarse: k * (d_anterior - d)
        reward_progress_mode: str = "total",  # "total": d_anterior con la plataforma anterior; "drone": solo lo que se movio el dron
        reward_pbrs_coef: float = 0.0,      # shaping por potencial: gamma * Phi(s') - Phi(s), Phi = -k * d (Ng et al. 1999)
        reward_pbrs_gamma: float = 0.99,    # tiene que ser el gamma de PPO para que el shaping no cambie la politica optima
        reward_action_coef: float = 0.0,    # castigo por cambiar la accion: c * sum((a - a_anterior)^2)
        reward_edge_coef: float = 0.0,      # castigo por estar bajo y afuera de la plataforma (modo de fallo de base)
        reward_descent_coef: float = 0.0,   # castigo por bajar mientras esta afuera de la plataforma y cerca en altura
        reward_cmd_vel_coef: float = 0.0,   # castigo por cambiar la velocidad pedida: c * |(v_cmd - v_cmd_anterior) / SPEED_LIMIT|^2
        reward_ang_vel_coef: float = 0.0,   # castigo por bamboleo: c * (wx^2 + wy^2), velocidad angular de roll y pitch
        reward_flare_coef: float = 0.0,     # castigo por bajar rapido justo encima del tope (alineado y a < 15 cm)
        landing_dxy_coef: float = 50.0,     # premio al aterrizar = 25 - landing_dxy_coef * d_xy (mas grande = premia mas el centro)
        landing_vz_coef: float = 0.0,       # premio extra al aterrizar = coef * (1 - v_bajada_al_tocar / SPEED_LIMIT)
        crash_penalty: float = 10.0,        # castigo al chocar

        # Accion
        action_mode: str = "direction",     # "direction": v = 0.6 * s * dir/|dir| (gym-pybullet-drones); "velocity": v = 0.6 * (dx, dy, dz)

        # Fisica
        ground_effect: bool = False,        # efecto suelo contra el tope de la plataforma y el piso (ver _groundEffect)
        ground_effect_scale: float = 1.0,   # multiplica el coeficiente de gym-pybullet-drones
    ):
        self.platform_radius = 0.25
        self.platform_height = 0.35
        self.linear_speed_range = linear_speed_range
        self.angular_speed_range = angular_speed_range
        self.vary_speed = vary_speed
        self.turt_noise = turt_noise
        self.spawn_xy_radius = spawn_xy_radius
        self.spawn_z_range = spawn_z_range
        self.reward_distance_coef = reward_distance_coef
        self.reward_dxy_coef = reward_dxy_coef
        self.reward_dz_coef = reward_dz_coef
        self.reward_progress_coef = reward_progress_coef
        self.reward_progress_mode = reward_progress_mode
        self.reward_pbrs_coef = reward_pbrs_coef
        self.reward_pbrs_gamma = reward_pbrs_gamma
        self.reward_action_coef = reward_action_coef
        self.reward_edge_coef = reward_edge_coef
        self.reward_descent_coef = reward_descent_coef
        self.reward_cmd_vel_coef = reward_cmd_vel_coef
        self.reward_ang_vel_coef = reward_ang_vel_coef
        self.reward_flare_coef = reward_flare_coef
        self.landing_dxy_coef = landing_dxy_coef
        self.landing_vz_coef = landing_vz_coef
        self.crash_penalty = crash_penalty
        self.ground_effect = ground_effect
        self.action_mode = action_mode
        self.ground_effect_scale = ground_effect_scale

        self.max_episode_steps = int(max_episode_seconds * ctrl_freq)

        # Limites
        self.turtle_v_max = 0.3 # m/s máximo
        self.turtle_w_max = 3.0 # rad/s máximo
        self.turtle_v_noise = 0.03 # ruido en velocidad lineal
        self.turtle_w_noise = 0.2 # ruido en velocidad angular

        # Escala de cada componente de la observacion (mismo orden que _computeObs). Las de velocidad se
        # derivan de los limites para que se ajusten solas si estos cambian.
        self._obs_scale = np.concatenate([
            np.full(3, OBS_POS_SCALE),                                         # pos relativa
            np.full(3, (DRONE_SPEED_LIMIT + self.turtle_v_max) * VEL_MARGIN),  # vel relativa: peor caso, en sentidos opuestos
            [OBS_ANGLE_SCALE, OBS_ANGLE_SCALE, np.pi],                         # roll, pitch, yaw
            np.full(3, OBS_ANG_VEL_SCALE),                                     # vel angular
            np.full(3, DRONE_SPEED_LIMIT * VEL_MARGIN),                        # vel del dron
            np.ones(4),                                                        # accion previa: ya en [-1, 1] y [0, 1]
        ]).astype(np.float32)

        self.linear_beta_params = (4, 2)
        self.angular_beta_params = (2, 4)
        self.spawn_xy_beta_params = (4, 2)

        self._rng = np.random.default_rng()

        initial_xyzs = np.array([[0.0, 0.0, 1.0]])

        super().__init__(
            drone_model=DroneModel.CF2X,
            num_drones=1,
            initial_xyzs=initial_xyzs,
            physics=Physics.PYB_GND if ground_effect else Physics.PYB,
            pyb_freq=240,
            ctrl_freq=ctrl_freq,
            gui=gui,
            record=False,
            obstacles=False,
        )
        self.SPEED_LIMIT = DRONE_SPEED_LIMIT

        self.action_space = spaces.Box(
            low=np.array([-1, -1, -1, 0], dtype=np.float32),
            high=np.array([1, 1, 1, 1], dtype=np.float32),
            dtype=np.float32,
        )

        obs, _ = self.reset()
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=obs.shape, dtype=np.float32)

    def _create_platform(self):
        radius = self.platform_radius
        height = self.platform_height

        col = p.createCollisionShape(
            shapeType=p.GEOM_CYLINDER,
            radius=radius,
            height=height,
            physicsClientId=self.CLIENT,
        )
        vis = p.createVisualShape(
            shapeType=p.GEOM_CYLINDER,
            radius=radius,
            length=height, # Cosa de PyBullet, el parámetro se llama length en vez de height
            rgbaColor=[0.15, 0.15, 0.15, 1.0],
            specularColor=[0, 0, 0],
            physicsClientId=self.CLIENT,
        )
        self.platform_id = p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=col,
            baseVisualShapeIndex=vis,
            basePosition=[0, 0, self.platform_height / 2],
            physicsClientId=self.CLIENT,
        )

        # Disco de arriba
        top_vis = p.createVisualShape(
            shapeType=p.GEOM_CYLINDER,
            radius=radius * 0.9,
            length=0.15,
            rgbaColor=[0.1, 0.8, 0.1, 0.4],  
            specularColor=[0, 0, 0],
            physicsClientId=self.CLIENT,
        )

        self.top_disc_id = p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=-1,  # Sin colision
            baseVisualShapeIndex=top_vis,
            basePosition=[0, 0, self.platform_height],
            physicsClientId=self.CLIENT,
        )

    def _sample_platform_params(self):
        self.platform_pos = np.array([0.0, 0.0, self.platform_height / 2])
        self.platform_vel = np.zeros(3)
        self.platform_yaw = self._rng.uniform(0, 2 * np.pi)

        self._sample_motion_params()

    def _sample_motion_params(self):
        self._linear_speed = self._beta_sample(self.linear_speed_range, *self.linear_beta_params)
        self._angular_speed = self._beta_sample(self.angular_speed_range, *self.angular_beta_params)
        self._angular_speed *= self._rng.choice([-1, 1])
        self._motion_step_count = 0

    def _beta_sample(self, range: tuple, alpha: float, beta: float) -> float:
        lo, hi = range
        return lo + self._rng.beta(alpha, beta) * (hi - lo)

    def _sample_drone_init(self) -> np.ndarray:
        r = self._beta_sample((self.platform_radius, self.spawn_xy_radius), *self.spawn_xy_beta_params)
        theta = self._rng.uniform(0, 2 * np.pi)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = self._rng.uniform(*self.spawn_z_range)
        return np.array([[x, y, z]])
    
    def _update_platform(self):
        dt = 1.0 / self.CTRL_FREQ

        if self.vary_speed:
            p_change = 1 - np.exp(-self._motion_step_count / 200)
            p_change = np.clip(p_change, 0.002, 0.15)

            if self._rng.random() < p_change:
                self._sample_motion_params()

        if self.turt_noise:
            self._linear_speed = np.clip(
                self._linear_speed + self._rng.uniform(-self.turtle_v_noise, self.turtle_v_noise),
                0.0,
                self.turtle_v_max,
            )
            self._angular_speed = np.clip(
                self._angular_speed + self._rng.uniform(-self.turtle_w_noise, self.turtle_w_noise),
                -self.turtle_w_max,
                self.turtle_w_max,
            )

        self._motion_step_count += 1

        self.platform_yaw += self._angular_speed * dt
        vx = self._linear_speed * np.cos(self.platform_yaw)
        vy = self._linear_speed * np.sin(self.platform_yaw)
        self.platform_pos[:2] += np.array([vx, vy]) * dt
        self.platform_pos[2] = self.platform_height / 2
        self.platform_vel = np.array([vx, vy, 0.0])

        p.resetBasePositionAndOrientation(
            self.platform_id,
            self.platform_pos.tolist(),
            [0, 0, 0, 1],
            physicsClientId=self.CLIENT,
        )
        p.resetBaseVelocity(
            self.platform_id,
            linearVelocity=self.platform_vel.tolist(),
            angularVelocity=[0, 0, 0],
            physicsClientId=self.CLIENT,
        )
        p.resetBasePositionAndOrientation(
            self.top_disc_id,
            [self.platform_pos[0], self.platform_pos[1], self.platform_height],
            [0, 0, 0, 1],
            physicsClientId=self.CLIENT,
        )

    def reset(self, seed=None, options=None):
        self.episode_step_counter = 0
        self.stable_counter = 0
        self._touching = False
        self._contact = None
        self.has_landed = False
        self.has_crashed = False
        self.is_truncated = False
        self.prev_action = np.zeros(4, dtype=np.float32)
        self._descent_speed = 0.0   # velocidad de bajada relativa al tope en el paso anterior (m/s, >= 0)
        self._touchdown_vz = None   # la de antes del primer contacto (como touchdown.vz de tools/evaluate.py)

        if seed is not None:
            self._rng = np.random.default_rng(seed)

        self._sample_platform_params()
        self.INIT_XYZS = self._sample_drone_init()

        obs, info = super().reset(seed=seed, options=options)
        # gym-pybullet-drones no reinicia el PID de VelocityAviary entre episodios: sin esto, cada episodio
        # arranca con el error integral y el ultimo angulo del anterior, y el resultado depende del orden.
        for ctrl in self.ctrl:
            ctrl.reset()

        self.platform_id = None
        self.top_disc_id = None
        self._create_platform()
        self._update_platform()

        # Antes se media contra el centro de la plataforma y no contra el tope (no importaba: el progreso
        # del primer paso no se cuenta).
        self.prev_drone_pos = self._getDroneStateVector(0)[0:3].copy()
        self.prev_d = np.linalg.norm(self.prev_drone_pos - self._platform_top())

        self._motion_step_count = 0

        return self._computeObs(), info

    def step(self, action):
        self._update_platform()

        action = np.array(action, dtype=np.float32).reshape(1, 4)
        if self.action_mode == "velocity":
            # La velocidad pedida es 0.6 * (dx, dy, dz), con norma <= 0.6: frenar es achicar la accion. Con "direction"
            # s queda saturado en 1 (media ~3) y la velocidad es siempre 0.6 m/s (tools/action_saturation.py). El cuarto
            # valor no se usa: se guarda en 0 para que no entre en la observacion ni en el castigo a la accion.
            action[0, 3] = 0.0
            v = self._commanded_velocity(action[0]) / self.SPEED_LIMIT
            speed = np.linalg.norm(v)
            vel_action = np.zeros((1, 4), dtype=np.float32)
            if speed > 0:
                vel_action[0, :3] = v / speed
                vel_action[0, 3] = speed
        else:
            vel_action = action
        self._current_action = action[0].copy()

        super().step(vel_action)

        self.episode_step_counter += 1

        self._contact = self._platform_contact()
        self._touching = (self._contact == 'top')
        if self._contact is not None and self._touchdown_vz is None:
            # Al final del paso con contacto, el choque ya freno al dron: se usa la del paso anterior.
            self._touchdown_vz = self._descent_speed
        self._update_stable_counter()
        self.has_landed = (self.stable_counter >= 10)
        self.has_crashed = self._crashed()
        terminated = (self.has_landed or self.has_crashed)
        self.is_truncated = (self.episode_step_counter >= self.max_episode_steps)

        reward = self._computeReward()

        self.prev_action = self._current_action.copy()
        self.prev_d = self._current_d
        self.prev_drone_pos = self._getDroneStateVector(0)[0:3].copy()
        self._descent_speed = max(0.0, -float(self._getDroneStateVector(0)[12] - self.platform_vel[2]))

        obs = self._computeObs()
        info = self._computeInfo()

        return obs, reward, terminated, self.is_truncated, info

    def _platform_top(self):
        return np.array([self.platform_pos[0], self.platform_pos[1], self.platform_height])

    def _computeObs(self):
        """Observacion normalizada a [-1, 1] con escalas fijas (self._obs_scale).

        En el robot real hay que aplicar exactamente esta misma cuenta sobre los valores de OptiTrack.
        """
        return np.clip(self._computeRawObs() / self._obs_scale, -1.0, 1.0).astype(np.float32)

    def _computeRawObs(self):
        """Observacion en unidades fisicas (m, m/s, rad, rad/s), sin normalizar."""
        state = self._getDroneStateVector(0)

        drone_pos = state[0:3]
        rpy = state[7:10]
        drone_vel = state[10:13]
        drone_ang_vel = state[13:16]

        rel_pos = drone_pos - np.array([self.platform_pos[0], self.platform_pos[1], self.platform_height])
        rel_vel = drone_vel - self.platform_vel

        obs = np.concatenate(
            [
                rel_pos,
                rel_vel,
                rpy,
                drone_ang_vel,
                drone_vel,
                self.prev_action,
            ]
        )

        return obs.astype(np.float32)
    
    def _computeReward(self):
        state = self._getDroneStateVector(0)
        drone_pos   = state[0:3]
        # roll, pitch = state[7:9]
        drone_vel   = state[10:13]

        platform_top = np.array([self.platform_pos[0], self.platform_pos[1], self.platform_height])
    
        rel_pos = drone_pos - platform_top
        rel_vel = drone_vel - self.platform_vel

        self._current_d = np.linalg.norm(rel_pos)
        d_xy = np.linalg.norm(rel_pos[0:2])

        # cosas viejas
        # v_target = self._get_target_velocity(rel_pos)
        # sq_err = np.sum((rel_vel - v_target)**2)
        # reward += 0.1 * (np.exp(-0.5 * sq_err) - 1.0)
        # reward -= 0.001 * (roll**2 + pitch**2) # estaba mal esta idea

        reward = 0.0

        # Castigo por distancia: se acumula mientras dure el episodio, asi que terminar rapido (chocando)
        # lo corta. Progreso: sumado en el episodio da k * (d_inicial - d_final), sin importar la duracion.
        reward -= self.reward_distance_coef * self._current_d
        # Separar horizontal y vertical permite que alinearse arriba de la plataforma valga mas que bajar.
        reward -= self.reward_dxy_coef * d_xy + self.reward_dz_coef * abs(rel_pos[2])
        reward -= 0.01
        if self.reward_progress_coef and self.episode_step_counter > 1:
            if self.reward_progress_mode == "drone":
                # Solo lo que se acerco el dron: las dos distancias contra el tope actual, asi el movimiento
                # de la plataforma no mete ruido (con "total", d cambia aunque el dron no haga nada).
                d_before = np.linalg.norm(self.prev_drone_pos - platform_top)
                reward += self.reward_progress_coef * (d_before - self._current_d)
            else:
                reward += self.reward_progress_coef * (self.prev_d - self._current_d)

        if self.reward_pbrs_coef:
            # Phi(s) = -k * d. En un estado terminal Phi = 0 (si no, deja de ser invariante); al truncar no,
            # porque PPO hace bootstrap con el valor del ultimo estado.
            phi_prev = -self.reward_pbrs_coef * self.prev_d
            phi_now = 0.0 if (self.has_landed or self.has_crashed) else -self.reward_pbrs_coef * self._current_d
            reward += self.reward_pbrs_gamma * phi_now - phi_prev

        if self.reward_action_coef and self.episode_step_counter > 1:
            reward -= self.reward_action_coef * float(np.sum((self._current_action - self.prev_action) ** 2))

        if self.reward_edge_coef:
            # v17/v21 chocan el borde bajando en diagonal desde afuera: castigar estar afuera del radio y a menos
            # de 15 cm del tope, proporcional a cuan afuera y cuan bajo.
            outside = max(0.0, d_xy - self.platform_radius)
            low = max(0.0, 0.15 - rel_pos[2])
            reward -= self.reward_edge_coef * outside * low / 0.15

        if self.reward_descent_coef:
            # Las politicas bajan siempre a velocidad maxima (dz saturado) y chocan el borde si llegan afuera.
            # Castiga la velocidad de bajada (no la posicion, como reward_edge_coef) estando afuera del radio y a
            # menos de 30 cm del tope: bajar alineado o lejos no cuesta nada, quedarse quieto tampoco.
            outside = max(0.0, d_xy - self.platform_radius)
            descending = max(0.0, -rel_vel[2])
            if rel_pos[2] < 0.3:
                reward -= self.reward_descent_coef * outside * descending / 0.1

        if self.reward_cmd_vel_coef and self.episode_step_counter > 1:
            # Como reward_action_coef, pero sobre la velocidad que se le pide al dron: la accion tiene una dimension
            # redundante (escalar la direccion no cambia la velocidad), y lo que siente el dron es el salto de velocidad.
            dv = (self._commanded_velocity(self._current_action) - self._commanded_velocity(self.prev_action)) / self.SPEED_LIMIT
            reward -= self.reward_cmd_vel_coef * float(np.sum(dv ** 2))

        if self.reward_ang_vel_coef:
            # Bamboleo del dron: velocidad angular de roll y pitch (rad/s). Moverse no cuesta; cambiar de inclinacion si.
            reward -= self.reward_ang_vel_coef * float(np.sum(state[13:15] ** 2))

        if self.reward_flare_coef:
            # Tocar suave: castiga bajar a mas de 0.15 m/s estando alineado (adentro del radio) y a menos de 15 cm del
            # tope. Las politicas llegan a tocar bajando a ~0.5 m/s (eval_*.json, touchdown.vz_median).
            if d_xy < self.platform_radius and 0.0 < rel_pos[2] < 0.15:
                reward -= self.reward_flare_coef * max(0.0, -rel_vel[2] - 0.15) / 0.1

        if self._is_touching_platform():
            reward += 0.1

        #terminales
        if self.has_landed:
            reward += 25.0 - d_xy * self.landing_dxy_coef
            if self.landing_vz_coef and self._touchdown_vz is not None:
                # Tocar suave: se paga una sola vez y solo si aterriza, asi que no encarece acercarse ni bajar
                # (los castigos por paso cerca del tope, como reward_flare_coef, caen en la trampa de flotar).
                reward += self.landing_vz_coef * max(0.0, 1.0 - self._touchdown_vz / self.SPEED_LIMIT)
        elif self.has_crashed:
            reward -= self.crash_penalty

        return float(reward)

    def _commanded_velocity(self, action):
        """Velocidad que se le pide al dron (m/s), con la misma cuenta que VelocityAviary._preprocessAction."""
        norm = np.linalg.norm(action[0:3])
        if self.action_mode == "velocity":
            return self.SPEED_LIMIT * np.asarray(action[0:3]) / max(1.0, norm)
        if norm == 0:
            return np.zeros(3)
        return self.SPEED_LIMIT * abs(action[3]) * action[0:3] / norm

    def _groundEffect(self, rpm, nth_drone):
        """Efecto suelo por helice, como BaseAviary._groundEffect pero con la altura sobre lo que haya debajo.

        El de gym-pybullet-drones mide la altura contra el piso (z = 0), y el tope esta a 0.35 m: ahi casi no
        empuja. Aca, la helice que esta encima de la plataforma mide contra el tope y la que esta afuera contra
        el piso, asi que cerca del borde aparece el efecto suelo parcial (algunas helices si, otras no).
        Empuje extra = KF * rpm^2 * GND_EFF_COEFF * (R / 4h)^2 (Shi et al. 2019); con el coeficiente de la CF2X y
        en hover da +4 % del peso a 10 cm, +15 % a 5 cm y +27 % desde 3.8 cm para abajo (GND_EFF_H_CLIP). Medido en
        un Crazyflie real puede ser bastante menos (~5 % a 4.6 cm): ver docs/estado-del-arte-2026-10-30.md.
        Solo se llama con Physics.PYB_GND (ground_effect=True).
        """
        link_states = p.getLinkStates(self.DRONE_IDS[nth_drone], linkIndices=[0, 1, 2, 3],
                                      physicsClientId=self.CLIENT)
        props = np.array([link_states[i][0] for i in range(4)])
        over_top = np.linalg.norm(props[:, :2] - self.platform_pos[:2], axis=1) < self.platform_radius
        heights = props[:, 2] - np.where(over_top, self.platform_height, 0.0)
        heights = np.clip(heights, self.GND_EFF_H_CLIP, np.inf)
        forces = (np.array(rpm) ** 2 * self.KF * self.GND_EFF_COEFF * self.ground_effect_scale
                  * (self.PROP_RADIUS / (4 * heights)) ** 2)
        if np.abs(self.rpy[nth_drone, 0]) < np.pi / 2 and np.abs(self.rpy[nth_drone, 1]) < np.pi / 2:
            for i in range(4):
                p.applyExternalForce(self.DRONE_IDS[nth_drone], i, forceObj=[0, 0, forces[i]], posObj=[0, 0, 0],
                                     flags=p.LINK_FRAME, physicsClientId=self.CLIENT)

    # Antes se usaba para velocity tracking, se puede borrar
    # def _get_target_velocity(self, rel_pos):
    #     v_max = 1.0
    #     v_target = -0.5 * rel_pos

    #     v_target_norm = np.linalg.norm(v_target)
    #     if v_target_norm > v_max:
    #         v_target = v_target / v_target_norm * v_max

    #     return v_target

    def _platform_contact(self):
        """'top' si todos los contactos son de la base del dron contra el tope de la plataforma, 'crash'
        si hay cualquier otro contacto, None si no toca nada.

        Antes se miraba solo la altura del punto (+-5 cm del tope), y un golpe contra el costado cerca del
        borde contaba como 'top'. La colision del CF2X es un cilindro (r=6 cm, alto 2.5 cm), sin patas.
        """
        contacts = p.getContactPoints(
            bodyA=self.DRONE_IDS[0],
            physicsClientId=self.CLIENT,
        )
        if not contacts:
            return None

        drone_pos, drone_quat = p.getBasePositionAndOrientation(self.DRONE_IDS[0], physicsClientId=self.CLIENT)
        drone_rot = np.array(p.getMatrixFromQuaternion(drone_quat)).reshape(3, 3)

        for contact in contacts:
            if contact[2] != self.platform_id:
                return 'crash'  # piso u otro cuerpo
            # contact[7]: normal sobre la plataforma, apuntando al dron. En el tope es +z; en el costado, horizontal.
            on_top = contact[7][2] > 0.9
            # contact[5]: punto sobre el dron. En su marco, la cara de abajo del cilindro esta en z = -0.0125.
            z_in_drone = (drone_rot.T @ (np.array(contact[5]) - np.array(drone_pos)))[2]
            with_bottom = z_in_drone < -0.01
            if not (on_top and with_bottom):
                return 'crash'

        return 'top'

    def _is_touching_platform(self):
        return self._contact == 'top'

    def _is_touching_ground(self):
        return self._contact == 'crash'

    def _update_stable_counter(self):
        state = self._getDroneStateVector(0)

        drone_pos = state[0:3]
        roll, pitch = state[7:9]
        drone_vel = state[10:13]

        rel_pos = drone_pos - self.platform_pos
        rel_vel = drone_vel - self.platform_vel

        d_xy = np.linalg.norm(rel_pos[0:2])
        vertical_speed = abs(rel_vel[2])

        conditions = (
            self._is_touching_platform()
            and d_xy < 0.2
            and vertical_speed < 0.1
            and abs(roll) < 0.1
            and abs(pitch) < 0.1
        )
        
        if conditions:
            self.stable_counter += 1
        else:
            self.stable_counter = 0
    
    def _landed_successfully(self):
        return self.stable_counter >= 10

    def _crashed(self):
        if self._contact == 'crash':
            return True
        
        state = self._getDroneStateVector(0)
        roll, pitch = state[7:9]

        return bool(abs(roll) > 0.7 or abs(pitch) > 0.7)

    def _computeInfo(self):
        state = self._getDroneStateVector(0)

        drone_pos = state[0:3]
        drone_vel = state[10:13]

        rel_pos = drone_pos - self.platform_pos
        rel_vel = drone_vel - self.platform_vel

        return {
            "is_success": self.has_landed, 
            "crashed": self.has_crashed,
            "d_xy": float(np.linalg.norm(rel_pos[0:2])),
            "dz": float(abs(drone_pos[2] - self.platform_height)),
            "v_rel": float(np.linalg.norm(rel_vel)),
            "vary_speed": self.vary_speed,
            "turt_noise": self.turt_noise,
        }