import numpy as np
import pybullet as p
from gymnasium import spaces

from gym_pybullet_drones.envs.VelocityAviary import VelocityAviary
from gym_pybullet_drones.utils.enums import DroneModel, Physics

# Velocidad maxima que se le pide al dron (m/s): accion = SPEED_LIMIT * s * direccion.
# VelocityAviary trae 0.25 m/s (3% de 30 km/h), menos que la plataforma (hasta 0.3 m/s), y el dron
# no podia alcanzarla. Tiene que ser el mismo limite que se use en el Crazyflie real (ver TODO_SIM2REAL.md).
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
    ):
        self.platform_radius = 0.25
        self.platform_height = 0.35
        self.linear_speed_range = linear_speed_range
        self.angular_speed_range = angular_speed_range
        self.vary_speed = vary_speed
        self.turt_noise = turt_noise
        self.spawn_xy_radius = spawn_xy_radius
        self.spawn_z_range = spawn_z_range

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
            physics=Physics.PYB,
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

        if seed is not None:
            self._rng = np.random.default_rng(seed)

        self._sample_platform_params()
        self.INIT_XYZS = self._sample_drone_init()

        obs, info = super().reset(seed=seed, options=options)

        self.platform_id = None
        self.top_disc_id = None
        self._create_platform()
        self._update_platform()

        rel_pos0 = self._getDroneStateVector(0)[0:3] - self.platform_pos
        self.prev_d = np.linalg.norm(rel_pos0)

        self._motion_step_count = 0

        return self._computeObs(), info

    def step(self, action):
        self._update_platform()

        action = np.array(action, dtype=np.float32).reshape(1, 4)
        self._current_action = action[0].copy()

        super().step(action)

        self.episode_step_counter += 1

        self._contact = self._platform_contact()
        self._touching = (self._contact == 'top')
        self._update_stable_counter()
        self.has_landed = (self.stable_counter >= 10)
        self.has_crashed = self._crashed()
        terminated = (self.has_landed or self.has_crashed)
        self.is_truncated = (self.episode_step_counter >= self.max_episode_steps)

        reward = self._computeReward()

        self.prev_action = self._current_action.copy()
        self.prev_d = self._current_d

        obs = self._computeObs()
        info = self._computeInfo()

        return obs, reward, terminated, self.is_truncated, info

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

        reward -= 0.1 * self._current_d
        reward -= 0.01

        # if self.episode_step_counter > 1:
        #     reward += 0.1 * (self.prev_d - self._current_d)
        #     da = np.sum((self._current_action - self.prev_action) ** 2)
        #     reward -= 0.02 * da  # alpha_action, punto de partida a tunear

        if self._is_touching_platform():
            reward += 0.1

        #terminales
        if self.has_landed:
            reward += 25.0 - d_xy * 50.0
        elif self.has_crashed:
            reward -= 10.0

        return float(reward)

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