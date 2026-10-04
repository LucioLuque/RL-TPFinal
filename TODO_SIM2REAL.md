# TODO sim2real

Qué falta para que una política entrenada en `env.py` tenga chances en el Crazyflie real aterrizando
sobre un turtlebot. Ordenado por prioridad. Cada cambio al entorno conviene hacerlo en una corrida
propia (registrada con `/registrar-corrida`), así se sabe qué efecto tuvo cada uno.

## 1. La plataforma no transmite el giro

**Hoy:** `_update_platform` mueve la plataforma reubicándola en cada paso de control (24 Hz). La
orientación es siempre `[0, 0, 0, 1]` y la velocidad angular que se le pasa es 0. El giro solo cambia
la dirección del avance: el cilindro no rota, y toda la superficie se mueve con la velocidad del centro.

Que se reubique en cada paso está bien: el dron apoyado acompaña a la plataforma porque
`resetBaseVelocity` le da la velocidad lineal para el rozamiento. **No sacar esa línea**: sin ella, el
dron queda quieto y la plataforma se va.

**Problema:** en un turtlebot real, el dron apoyado gira con el robot. Además, un punto fuera del
centro se mueve más rápido: a 20 cm del centro y 2.84 rad/s, son 0.57 m/s más que el centro.

**Arreglo:** en `_update_platform`, usar `p.getQuaternionFromEuler([0, 0, self.platform_yaw])` como
orientación y pasar `angularVelocity=[0, 0, self._angular_speed]` a `resetBaseVelocity`. Hacer lo mismo
con `top_disc_id`.

**Evidencia (2026-10-03):** simulación en PyBullet con una caja de 27 g apoyada a 15 cm del centro, con
v = 0.2 m/s y ω = 2.84 rad/s:

| | Hoy | Rotando la plataforma |
|---|---|---|
| ¿La caja gira con la plataforma? | No (0° contra 128°) | Sí |
| Error contra movimiento rígido | 18 cm en promedio y crece | 5–7 cm, constante (resbala solo al arrancar) |

Reubicar la plataforma a 240 Hz en vez de 24 Hz mejora poco (de 7 a 5 cm), así que no hace falta.

- [ ] Implementar y entrenar una corrida.

## 2. Efecto suelo, resistencia del aire y downwash

**Hoy:** `physics=Physics.PYB`, que no modela el efecto suelo, la resistencia del aire ni el downwash
(el flujo de aire hacia abajo de las hélices).

**Problema:** cerca de una superficie, el efecto suelo es fuerte en un Crazyflie: el dron flota y
rebota justo antes de tocar la plataforma. Es exactamente la fase que más importa.

**Arreglo:** `Physics.PYB_GND_DRAG_DW`, que ya viene en gym-pybullet-drones.

**Ojo (verificado el 2026-10-03):** `BaseAviary._groundEffect` usa la altura absoluta de las hélices
(`link_states[i][0][2]`), o sea que lo calcula contra el piso (z = 0) y no contra la plataforma, que
está a 35 cm. Así como viene, sobre la plataforma prácticamente no hay efecto suelo. Hay que
sobrescribir `_groundEffect` en `env.py` para que, cuando el dron está sobre la plataforma, use la
altura respecto del tope.

- [x] Ver cómo calcula la librería el efecto suelo.
- [ ] Sobrescribir `_groundEffect` y entrenar una corrida.

## 3. Observación perfecta

**Hoy:** `_computeObs` usa la posición y velocidad exactas del dron y de la plataforma.

**Problema:** en el robot real, la posición del dron y del turtlebot viene de OptiTrack. La posición
es muy precisa (en general, error submilimétrico), pero:
- **la velocidad no la mide OptiTrack:** hay que calcularla derivando la posición (o filtrándola), y
  eso es más ruidoso y tiene más retraso. La velocidad relativa es la parte más delicada de la
  observación;
- **hay retraso:** OptiTrack → PC → política → radio → Crazyflie;
- **se puede perder el tracking** algunos frames, por ejemplo si se tapan los marcadores.

**Arreglo:** agregar ruido y retraso a la observación (ver domain randomization). Lo más fiel es
simular el mismo pipeline: ruido chico en la posición y velocidad calculada igual que en el sistema
real (misma derivada y mismo filtro), en vez de ruido inventado sobre la velocidad exacta.

- [ ] Definir cómo se va a calcular la velocidad en el sistema real (derivada, filtro).
- [ ] Agregar ruido y retraso a la observación, replicando ese cálculo.

## 4. ⚠️ IMPORTANTE: frecuencias de OptiTrack, de la política y del Crazyflie

**Hoy:** la política se entrena a 24 Hz (`DEFAULT_CTRL_FREQ` en `utils.py`): ve una observación y
manda una acción cada 1/24 s. La física corre a 240 Hz.

**Problema:** la política aprende la dinámica de un paso de 1/24 s. Si en el robot real corre a otra
frecuencia, cada acción dura otro tiempo, y la acción previa que está en la observación significa
otra cosa. Además, la frecuencia real queda limitada por la más lenta de la cadena:

| Eslabón | Frecuencia | A completar |
|---|---|---|
| OptiTrack (captura) | ? Hz | Configurado en Motive |
| Envío de OptiTrack a la PC (streaming) | ? Hz | |
| Bucle de la política en la PC | ? Hz | Tiene que ser 24 Hz, o reentrenar a la que se elija |
| Comandos por radio al Crazyflie | ? Hz | cflib / Crazyswarm |
| Controlador interno del Crazyflie | ? Hz | Firmware |
| Latencia total, de la captura al motor | ? ms | Medir de punta a punta |

**Arreglo:**
1. Medir o averiguar cada fila.
2. Elegir la frecuencia de la política según la más lenta de la cadena (con margen) y entrenar a
   esa misma frecuencia (`DEFAULT_CTRL_FREQ`).
3. Usar la latencia medida para los rangos de retraso del domain randomization.

- [ ] Completar la tabla.
- [ ] Ajustar `DEFAULT_CTRL_FREQ` si hace falta.

### Límite de velocidad del dron: tiene que coincidir con el real

**Hoy:** `DRONE_SPEED_LIMIT = 0.6` m/s en `env.py` (antes era 0.25, el valor de la librería; ver
`BITACORA.md`, 2026-10-03). La acción se convierte en una velocidad pedida con
`SPEED_LIMIT · s · dirección normalizada`.

**En el Crazyflie real** (firmware de Bitcraze, rama master, revisado el 2026-10-03):
- En modo velocidad (mandando `vx`, `vy`, `vz`), el firmware no recorta la velocidad. Lo que limita es la
  inclinación máxima (`velCtlPid.rLimit` y `pLimit`, 20° por defecto), es decir, la aceleración.
- En modo posición, el límite es de 1.0 m/s por eje (`posCtlPid.xVelMax` y demás).

Entonces el límite lo tiene que aplicar el código que manda los comandos, con la misma fórmula que la
simulación.

- [ ] Implementar en el código del robot real la misma conversión acción → velocidad, con 0.6 m/s.
- [ ] Verificar que el Crazyflie real sigue velocidades de hasta 0.6 m/s sin saturar la inclinación
  (comparar la velocidad medida por OptiTrack con la pedida).
- [ ] Verificar que 0.6 m/s es seguro en el volumen de OptiTrack del laboratorio.

## 5. Cambios de velocidad instantáneos

**Hoy:** `_sample_motion_params` cambia la velocidad lineal y angular de golpe cuando `vary_speed`
sortea un cambio. `turt_noise` suma ruido uniforme en cada paso.

**Problema:** un turtlebot real tiene límites de aceleración y su controlador sigue los comandos con
cierto retardo. Los saltos instantáneos son más difíciles que lo real, lo cual no está mal, pero no
representan la dinámica real.

**Arreglo:** que la velocidad sorteada sea el *objetivo*, y que la velocidad actual se acerque a ese
objetivo con una aceleración máxima. Referencia del TurtleBot3 Burger: 0.22 m/s y 2.84 rad/s
máximos; falta medir su aceleración.

Los rangos actuales (0.05–0.3 m/s, 0–3 rad/s) superan los máximos reales a propósito, para dar
robustez. Está bien dejarlos así.

- [ ] Medir la aceleración del turtlebot real, o sacarla de la documentación.
- [ ] Implementar el límite de aceleración.

## 6. Domain randomization

Que en cada episodio los parámetros del simulador cambien un poco, para que la política no dependa de
valores exactos que en la realidad son distintos.

**Ya se randomiza:** la posición inicial del dron, la orientación inicial de la plataforma, las
velocidades lineal y angular, los cambios de velocidad durante el episodio y el ruido en la velocidad
de la plataforma.

**Para agregar.** Las prioridades son sugeridas y los rangos son puntos de partida, a ajustar:

| Prioridad | Qué | Por qué | Rango inicial |
|---|---|---|---|
| Alta | Ruido de observación | OptiTrack y el cálculo de la velocidad (ver punto 3) | Posición: σ ≈ 1 mm; velocidad: la que resulte de derivar esa posición |
| Alta | Retraso de la observación | Cadena OptiTrack → PC (ver punto 4) | Alrededor de la latencia medida; arrancar con 0–2 pasos (0–80 ms a 24 Hz) |
| Alta | Pérdida de tracking | Marcadores tapados | Repetir la última observación durante 1–3 pasos, con probabilidad baja |
| Alta | Retraso de la acción | Retardo del radio del Crazyflie | 0–1 paso |
| Alta | Masa del dron | Batería, agregados, distintas unidades | ±10–15 % (`self.M`, y `p.changeDynamics` en el cuerpo) |
| Media | Empuje de los motores (`self.KF`) | Desgaste, batería que se descarga | ±10 % |
| Media | Rozamiento de la plataforma | Material real desconocido | 0.5–1.2 (`p.changeDynamics(..., lateralFriction=)`) |
| Media | Perturbaciones externas (viento, golpes) | Corrientes de aire en el lugar | Fuerza aleatoria chica cada tanto (`p.applyExternalForce`) |
| Media | Aceleración del turtlebot | Ver punto 5 | Alrededor de lo medido |
| Baja | Coeficientes de efecto suelo y resistencia | El modelo no es exacto | ±20 % |
| Baja | Frecuencia de control | Variaciones de timing en el sistema real (ver punto 4) | Frecuencia elegida ± jitter chico |

**Cómo agregarla sin romper el entrenamiento:** de a uno o dos parámetros por corrida, empezando por
los de prioridad alta. Si el éxito cae mucho, ampliar los rangos de forma progresiva durante el
entrenamiento.

- [ ] Ruido y retraso de observación y acción.
- [ ] Masa y empuje.
- [ ] El resto, según lo que muestren las pruebas reales.
