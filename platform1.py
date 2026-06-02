import numpy as np
import pybullet as p
from gymnasium import spaces

from gym_pybullet_drones.envs.VelocityAviary import VelocityAviary
from gym_pybullet_drones.utils.enums import DroneModel, Physics

PLATFORM_MODES = ("static", "linear", "turtlebot")


class MovingPlatformLandingAviary(VelocityAviary):
    def __init__(
        self,
        mode: str = "static",
        gui: bool = False,
        ctrl_freq: int = 48,
        max_episode_seconds: int = 8,
        platform_radius: float = 0.18,
        platform_z: float = 0.02,
        
        # linear
        linear_speed_range: tuple = (0.1, 0.4),   # m/s (min, max)
        
        # turtlebot
        turtle_linear_speed_range: tuple = (0.1, 0.3),   # m/s
        turtle_angular_speed_range: tuple = (0.2, 0.8),  # rad/s
    
        # dron 
        drone_init_xy_range: float = 0.8,  # radio máximo en XY (m)
        drone_init_z_range: tuple = (0.5, 1.5),  # altura inicial (m)
    ):
        self.mode = mode
        self.platform_radius = platform_radius
        self.platform_z = platform_z
        self.linear_speed_range = linear_speed_range
        self.turtle_linear_speed_range = turtle_linear_speed_range
        self.turtle_angular_speed_range = turtle_angular_speed_range
        self.drone_init_xy_range = drone_init_xy_range
        self.drone_init_z_range = drone_init_z_range
 
        self.episode_step_counter = 0
        self.max_episode_steps = int(max_episode_seconds * ctrl_freq)
 
        self.platform_id = None
        self.platform_pos = np.zeros(3)
        self.platform_vel = np.zeros(3)
        self.platform_yaw = 0.0           # solo usado en modo turtlebot
 
        # Parámetros que se re-sortean en cada reset
        self._linear_direction = np.zeros(2)  # modo linear
        self._linear_speed = 0.0              # modo linear
        self._turtle_v = 0.0
        self._turtle_w = 0.0
        self.platform_yaw = 0.0

        # Límites
        self.turtle_v_max = 0.3        # m/s máximo
        self.turtle_w_max = 2.0        # rad/s máximo
        self.turtle_v_noise = 0.03     # qué tan bruscamente cambia la velocidad lineal
        self.turtle_w_noise = 0.2     # qué tan bruscamente cambia la dirección
 
        self.stable_counter = 0
        self._turtle_step_count = 0
        self._prev_d_total = None

        self._touching = False
        self.has_landed = False
        self.has_crashed = False
        self.is_truncated = False

        self._prev_p  = None
        self._prev_v  = None
        self._prev_th = None
 
        # Posición inicial del dron (se actualiza en reset)
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

        obs_low = np.full(12, -np.inf, dtype=np.float32)
        obs_high = np.full(12, np.inf, dtype=np.float32)

        self.observation_space = spaces.Box(
            low=obs_low,
            high=obs_high,
            dtype=np.float32,
        )

        self.action_space = spaces.Box(
            low=np.array([-1, -1, -1, 0], dtype=np.float32),
            high=np.array([1, 1, 1, 1], dtype=np.float32),
            dtype=np.float32,
        )

        self._create_platform()

    def _create_platform(self):
        half_extents = [self.platform_radius, self.platform_radius, 0.01]
 
        col = p.createCollisionShape(
            shapeType=p.GEOM_BOX,
            halfExtents=half_extents,
            physicsClientId=self.CLIENT,
        )
        vis = p.createVisualShape(
            shapeType=p.GEOM_BOX,
            halfExtents=half_extents,
            rgbaColor=[0.1, 0.8, 0.1, 1.0],
            physicsClientId=self.CLIENT,
        )
        self.platform_id = p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=col,
            baseVisualShapeIndex=vis,
            basePosition=[0, 0, self.platform_z],
            physicsClientId=self.CLIENT,
        )

    def _update_platform(self):
        dt = 1.0 / self.CTRL_FREQ
 
        if self.mode == "static":
            # La plataforma no se mueve; pos y vel ya están seteados en reset.
            pass
 
        elif self.mode == "linear":
            new_xy = self.platform_pos[:2] + self._linear_direction * self._linear_speed * dt
            self.platform_pos = np.array([new_xy[0], new_xy[1], self.platform_z])
            self.platform_vel = np.array([
                self._linear_direction[0] * self._linear_speed,
                self._linear_direction[1] * self._linear_speed,
                0.0,
            ])
 
        elif self.mode == "turtlebot":
            # Probabilidad de cambiar acción crece con el tiempo
            # Al step 0: prob ≈ 0.002, al step 480 (10s a 48Hz): prob ≈ 0.08
            p_change = 1 - np.exp(-self._turtle_step_count / 200)  # 200 = "velocidad" del crecimiento
            p_change = np.clip(p_change, 0.002, 0.15)              # mínimo y máximo de prob por step

            rng = getattr(self, "_rng", np.random.default_rng())

            if rng.random() < p_change:
                self._turtle_v += rng.uniform(-self.turtle_v_noise, self.turtle_v_noise)
                self._turtle_w += rng.uniform(-self.turtle_w_noise, self.turtle_w_noise)
                self._turtle_v = np.clip(self._turtle_v, -self.turtle_v_max, self.turtle_v_max)
                self._turtle_w = np.clip(self._turtle_w, -self.turtle_w_max, self.turtle_w_max)
                self._turtle_step_count = 0  # resetear contador de pasos desde último cambio

            self._turtle_step_count += 1

            self.platform_yaw += self._turtle_w * dt
            vx = self._turtle_v * np.cos(self.platform_yaw)
            vy = self._turtle_v * np.sin(self.platform_yaw)
            self.platform_pos[:2] += np.array([vx, vy]) * dt
            self.platform_pos[2] = self.platform_z
            self.platform_vel = np.array([vx, vy, 0.0])
 
        # Mover el cuerpo cinemático en PyBullet y setear su velocidad lineal
        # para que el motor de contactos la tenga en cuenta.
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

    def _sample_platform_params(self, rng: np.random.Generator):
        """Sortea parámetros de movimiento según el modo activo."""
        if self.mode == "static":
            self.platform_pos = np.array([0.0, 0.0, self.platform_z])
            self.platform_vel = np.zeros(3)
 
        elif self.mode == "linear":
            speed = rng.uniform(*self.linear_speed_range)
            angle = rng.uniform(0, 2 * np.pi)
            self._linear_direction = np.array([np.cos(angle), np.sin(angle)])
            self._linear_speed = speed
            # Empezar la plataforma en el origen
            self.platform_pos = np.array([0.0, 0.0, self.platform_z])
            self.platform_vel = np.array([
                self._linear_direction[0] * speed,
                self._linear_direction[1] * speed,
                0.0,
            ])
 
        elif self.mode == "turtlebot":
            self._turtle_v = rng.uniform(-0.2, 0.2)
            self._turtle_w = rng.uniform(-0.3, 0.3)
            self.platform_yaw = rng.uniform(0, 2 * np.pi)
            self.platform_pos = np.array([0.0, 0.0, self.platform_z])
            self.platform_vel = np.zeros(3)

    def _sample_drone_init(self, rng: np.random.Generator) -> np.ndarray:
        """Posición inicial aleatoria del dron."""
        r = rng.uniform(0, self.drone_init_xy_range)
        theta = rng.uniform(0, 2 * np.pi)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = rng.uniform(*self.drone_init_z_range)
        return np.array([[x, y, z]])

    def reset(self, seed=None, options=None):
        self.episode_step_counter = 0
        self.stable_counter = 0
        self._touching = False
        self.has_landed = False
        self.has_crashed = False
        self.is_truncated = False
        self._prev_d_total = None
 
        self._rng = np.random.default_rng(seed)
        rng = self._rng
 
        # Sortear parámetros de movimiento de la plataforma
        self._sample_platform_params(rng)
 
        # Sortear posición inicial del dron
        self.INIT_XYZS = self._sample_drone_init(rng)
 
        obs, info = super().reset(seed=seed, options=options)
 
        # Recrear la plataforma (el super().reset() limpia el mundo)
        self.platform_id = None
        self._create_platform()
        self._update_platform()


        self._prev_p  = None
        self._prev_v  = None
        self._prev_th = None
 
        return self._computeObs(), info

    def step(self, action):
        self._update_platform()

        action = np.array(action, dtype=np.float32).reshape(1, 4)

        obs, reward, terminated, truncated, info = super().step(action)

        self.episode_step_counter += 1
        
        self._update_stable_counter()
        self._touching = self._is_touching_platform()
        self.has_landed = self._landed_successfully()
        self.has_crashed = self._crashed()
        self.is_truncated = self.episode_step_counter >= self.max_episode_steps

        return self._computeObs(),self._computeReward(), self._computeTerminated(), self._computeTruncated(), self._computeInfo()

    def _computeObs(self):
        state = self._getDroneStateVector(0)

        drone_pos = state[0:3]
        rpy = state[7:10]
        drone_vel = state[10:13]
        drone_ang_vel = state[13:16]

        rel_pos = drone_pos - self.platform_pos
        rel_vel = drone_vel - self.platform_vel

        obs = np.concatenate(
            [
                rel_pos,
                rel_vel,
                rpy,
                drone_ang_vel,
                # self.platform_vel[0:2],
            ]
        )

        return obs.astype(np.float32)
    

    # def _computeReward(self):
    #     state = self._getDroneStateVector(0)

    #     drone_pos = state[0:3]
    #     rpy = state[7:10]
    #     drone_vel = state[10:13]

    #     rel_pos = drone_pos - self.platform_pos
    #     rel_vel = drone_vel - self.platform_vel

    #     p_x = np.linalg.norm(rel_pos)
    #     v_x = np.linalg.norm(rel_vel)

    #     w_p    = -1.0
    #     w_v    = -0.5
    #     # w_w    = -0.3   # w_theta
    #     w_dur  = -0.1
    #     w_suc  =  5.0
    #     w_fail = -5.0

    #     # Límites del escenario
    #     v_lim     = 1.0   # velocidad máxima esperada (m/s)
    #     a_lim     = 1.0   # aceleración máxima esperada (m/s²)
    #     # theta_max = 0.8   # rad
    #     delta_t   = 1.0 / self.CTRL_FREQ

    #     r_p_max   = abs(w_p) * v_lim * delta_t
    #     r_v_max   = abs(w_v) * a_lim * delta_t
    #     # r_th_max  = abs(w_w) * v_lim * (delta_t / theta_max)   # Δθ/θ_max escalado
    #     r_dur_max = abs(w_dur) * v_lim * delta_t

    #     r_max = r_p_max + r_v_max + r_dur_max

    #     delta_p = 0.0 if self._prev_p is None else (p_x - self._prev_p)
    #     delta_v = 0.0 if self._prev_v is None else (v_x - self._prev_v)


    #     self._prev_p = p_x
    #     self._prev_v = v_x

    #     r_p   = float(np.clip(w_p * delta_p, -r_p_max, r_p_max))
    #     r_v   = float(np.clip(w_v * delta_v, -r_v_max, r_v_max))
    #     r_dur = w_dur * v_lim * delta_t



    #     if self.has_landed:
    #         r_term = w_suc * r_max
    #     elif self.has_crashed or self.is_truncated:
    #         r_term = w_fail * r_max
    #     else:
    #         r_term = 0.0

    #     return float(r_p + r_v + r_dur + r_term)

    def _computeReward(self):
        state = self._getDroneStateVector(0)
        drone_pos = state[0:3]
        rpy       = state[7:10]
        drone_vel = state[10:13]

        rel_pos = drone_pos - self.platform_pos
        rel_vel = drone_vel - self.platform_vel

        d_total = np.linalg.norm(rel_pos)
        v_total = np.linalg.norm(rel_vel)
        roll, pitch, _ = rpy

        reward = 0.0

        # Señal densa: distancia (siempre activa, escala razonable)
        reward -= 0.5 * np.clip(d_total / 2.0, 0.0, 1.0)

        # Penalización por velocidad relativa alta cerca de la plataforma
        if d_total < 0.5:
            reward -= 0.2 * np.clip(v_total / 2.0, 0.0, 1.0)

        # Penalización por inclinación
        reward -= 0.1 * np.clip((abs(roll) + abs(pitch)) / 0.8, 0.0, 1.0)

        # Penalización por tiempo (apura al agente)
        reward -= 0.01

        # Terminal
        if self.has_landed:
            reward += 10.0
        elif self.has_crashed:
            reward -= 5.0
        elif self.is_truncated:
            reward -= 2.0

        return float(reward)

    def _is_touching_platform(self):
        contacts = p.getContactPoints(
            bodyA=self.DRONE_IDS[0],
            bodyB=self.platform_id,
            physicsClientId=self.CLIENT,
        )
        return len(contacts) > 0

    def _is_touching_ground(self):
        contacts = p.getContactPoints(
            bodyA=self.DRONE_IDS[0],
            physicsClientId=self.CLIENT,
        )
        if not contacts:
            return False
        for contact in contacts:
            if contact[2] != self.platform_id:
                return True
        return False


    def _update_stable_counter(self):
        state = self._getDroneStateVector(0)

        drone_pos = state[0:3]
        rpy = state[7:10]
        drone_vel = state[10:13]

        rel_pos = drone_pos - self.platform_pos
        rel_vel = drone_vel - self.platform_vel

        d_xy = np.linalg.norm(rel_pos[0:2])
        vertical_speed = abs(rel_vel[2])

        roll, pitch, _ = rpy

        conditions = (
            self._is_touching_platform()
            # and d_xy < 0.15
            and vertical_speed < 0.35
            and abs(roll) < 0.35
            and abs(pitch) < 0.35
        )
        # pondria diferencia a la inclinacion de la plataforma
        
        if conditions:
            self.stable_counter += 1
        else:
            self.stable_counter = 0
    
    def _landed_successfully(self):
        return self.stable_counter >= 10

    def _crashed(self):
        state = self._getDroneStateVector(0)

        rpy = state[7:10]

        roll, pitch, _ = rpy

        too_tilted = abs(roll) > 0.8 or abs(pitch) > 0.8
        hit_ground = self._is_touching_ground()

        return too_tilted or hit_ground

    # def _out_of_bounds(self):
    #     state = self._getDroneStateVector(0)

    #     x, y, z = state[0:3]

    #     return abs(x) > 2.0 or abs(y) > 2.0 or z > 2.0

    def _computeTerminated(self):
        return bool(
            self.has_landed or self.has_crashed
            # or self._out_of_bounds()
        )

    def _computeTruncated(self):
        return bool(self.is_truncated)

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
            "dz": float(abs(rel_pos[2])),
            "v_rel": float(np.linalg.norm(rel_vel)),
            "mode": self.mode,
        }