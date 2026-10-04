# RL-TPFinal

TP final de RL (UdeSA), hecho entre dos: Lucio y Teo. Un dron Crazyflie (CF2X) aprende a aterrizar sobre
una plataforma con forma de turtlebot, que se mueve. Se usa PPO de stable-baselines3 sobre gym-pybullet-drones.
Dependencias directas en `requirements.txt` (cómo crear el entorno conda `drone-landing` está arriba de ese
archivo). gym-pybullet-drones (2.2.0) se instala desde GitHub, fijado a un commit, porque no está en PyPI.

## Comandos

```bash
python train.py                                  # corrida nueva -> v<N>-<autor>
python train.py --load v16-lucio --timesteps 500000   # seguir entrenando una corrida
python eval.py --load v16-lucio --episodes 5     # con GUI; sin --load usa la última
python -m tools.evaluate --load v17-lucio --best # 100 episodios sin GUI -> runs/<id>/eval_best.json
python -m tools.generate_gif --load v16-lucio    # gif de un episodio en media/gifs/
python -m tools.plot_trajectory --load v16-lucio
python -m tools.plots                            # curvas de TensorBoard (editar el __main__)
python -m tools.experiments_index                # regenera EXPERIMENTS.md
```

Todo se corre desde la raíz del repo: las rutas son relativas a ella, y los scripts de `tools/` se corren con `-m` para que encuentren `utils`.

## Estructura

- Raíz: núcleo (`env.py`, `train.py`, `eval.py`, `utils.py`, `run_registry.py`, `levels.yaml`).
- `runs/<id>/`: todo lo de una corrida (ver abajo).
- `tools/`: análisis (gifs, trayectorias, curvas, índice de experimentos).
- `media/`: gifs y plots para el informe o la presentación.
- `docs/`: consigna, informe y presentación.
- `logs/landing_level_1/`: TensorBoard de las corridas de curriculum viejas. `logs/` está en
  `.gitignore`; los logs de `version_N` van en `runs/version_N/tb/`.

`--load` acepta `v16-lucio` (corridas nuevas) o `15` (las viejas, que en disco se llaman `version_15`).

## Corridas y registro

- **Id**: `v<N>-<autor>`. N es global entre los dos autores (el mayor existente + 1). El autor es la
  primera palabra de `git config user.name`. Hacer `git pull` antes de entrenar.
- **`runs/<id>/`** tiene todo lo de una corrida, y lo escribe `train.py` solo:
  - `model.zip`: el modelo final;
  - `best/best_model.zip`: el mejor por tasa de éxito y, si empatan, por reward;
  - `run.json`: args, hiperparámetros, entorno, git, resultados y evals;
  - `diff.patch`: lo no commiteado; copias de `env.py` y `levels.yaml`;
  - `tb/`: TensorBoard (se commitea, para que los dos puedan graficar cualquier corrida con `tools/plots.py`).

  `eval.py`, `generate_gif.py` y `plot_trajectory.py` cargan el modelo final, no el best.
- **Después de cada entrenamiento, correr `/registrar-corrida`**: escribe `runs/<id>/NOTES.md` y regenera
  `EXPERIMENTS.md`, que es el índice de todas las corridas. Antes de proponer un cambio de reward,
  observación o hiperparámetros, leer `EXPERIMENTS.md` y las notas de las últimas corridas, para no
  repetir algo que ya se probó.
- **`BITACORA.md`**: ideas, decisiones y observaciones que no son de una sola corrida, con fecha y autor.
  Leerla junto con `EXPERIMENTS.md` antes de proponer cambios. Agregar entradas solo cuando lo pidan.
- **`TODO.md`**: pendientes generales, en orden. Marcar las tareas a medida que se hacen.
- **`TODO_SIM2REAL.md`**: pendientes para pasar la política al turtlebot real (giro de la plataforma,
  efecto suelo, observación de OptiTrack, frecuencias de la cadena real, aceleración del turtlebot y
  domain randomization). La meta final es el robot real: tenerlo en cuenta al proponer cambios al entorno.
- `EXPERIMENTS.md` es generado: no editarlo a mano. Si tiene un conflicto de merge, regenerarlo.
- Las corridas `version_1` a `version_15` y `landing_level_1/2` son anteriores al registro: en `runs/`
  solo tienen `model.zip` y `vecnormalize.pkl`. No se pueden cargar con el código actual (otra
  observación y `VecNormalize`).

## Entorno (`env.py`, `MovingPlatformLandingAviary`)

- **Acción** (VelocityAviary): `[dx, dy, dz] ∈ [-1, 1]` es la dirección y `s ∈ [0, 1]` la fracción de la velocidad máxima
  (`DRONE_SPEED_LIMIT = 0.6` m/s en `env.py`; tiene que coincidir con el límite del Crazyflie real).
- **Observación** (19 dimensiones): pos relativa al tope de la plataforma (3), vel relativa (3), rpy (3),
  vel angular (3), vel del dron (3) y acción previa (4). Se normaliza a [-1, 1] con escalas fijas
  (`_obs_scale`, constantes `OBS_*` en `env.py`); `_computeRawObs` da los valores físicos. No se usa
  `VecNormalize`, y la recompensa va sin normalizar.
- **Nivel**: siempre `turtlebot_hard_fixed` (`utils.LEVEL`, en `levels.yaml`). Los niveles de curriculum
  viejos ya no se usan.
- **Éxito**: 10 steps seguidos tocando el tope de la plataforma, con `d_xy < 0.2`, `|vz_rel| < 0.1` y `|roll|, |pitch| < 0.1`.
- **Contacto** (`_platform_contact`): `top` solo si todos los puntos son de la base del dron contra el tope
  (normal hacia arriba); cualquier otro contacto es choque. El CF2X no tiene patas: su colisión es un
  cilindro de 12 cm × 2.5 cm.
- **Choque**: contacto que no sea base contra tope, o `|roll|` o `|pitch|` mayor a 0.7.
- **Truncado**: a los 20 s (24 Hz, 480 steps).
- **Reward**: ver `_computeReward`. Hay términos comentados de pruebas anteriores. Ojo: el commit
  `f94b2d3` dice que agrega una penalización por cambios de acción, pero está comentada.

## Convenciones

- Comentarios y mensajes en español.
- La selección del mejor modelo es por tasa de éxito, no por reward (ver el docstring de `BestModelCallback`).
- Con 8 episodios de evaluación, la tasa de éxito va de a 12.5%: no sacar conclusiones de un episodio de diferencia.
- Todo `runs/` se commitea (modelos y TensorBoard), porque es chico y el otro los necesita para evaluar. Los gifs se commitean solo si van al informe.
