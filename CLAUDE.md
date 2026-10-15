# RL-TPFinal

TP final de RL (UdeSA), hecho entre dos: Lucio y Teo. Un dron Crazyflie (CF2X) aprende a aterrizar sobre
una plataforma con forma de turtlebot, que se mueve. Se usa PPO de stable-baselines3 sobre gym-pybullet-drones.
Dependencias directas en `requirements.txt` (cómo crear el entorno conda `drone-landing` está arriba de ese
archivo). gym-pybullet-drones (2.2.0) se instala desde GitHub, fijado a un commit, porque no está en PyPI.

## Comandos

```bash
python train.py                                  # corrida nueva -> v<N>-<autor>, recompensa suave_bajada
python train.py --reward base --seed 1 --log_std_init -0.5   # otra recompensa, seed y desvío inicial
python train.py --load v16-lucio --timesteps 500000   # seguir entrenando una corrida (con su recompensa)
python eval.py --load v16-lucio --episodes 5     # con GUI; sin --load usa la última
python -m tools.evaluate --load v17-lucio --best # 100 episodios sin GUI -> runs/<id>/eval_best.json
python -m tools.evaluate --load v17-lucio        # lo mismo con el modelo final -> eval_final.json
python -m tools.run_queue cola_pendiente.txt --parallel 2   # cola de corridas en paralelo + evaluaciones
python -m tools.compare_runs v54-lucio v56-lucio --by-reward --plot media/plots/x.png   # tabla y curvas
python -m tools.action_saturation v54-lucio      # cuánto satura la acción (bang-bang)
python -m tools.plot_actions v40-lucio v54-lucio # velocidad pedida paso a paso
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
- `docs/`: consigna, informe, presentación y reportes de experimentos (`pruebas-recompensas-2026-10-15.md`).
- `cola_pendiente.txt`: corridas planeadas que no se corrieron todavía (para `tools/run_queue.py`).
- `logs/landing_level_1/`: TensorBoard de las corridas de curriculum viejas. `logs/` está en
  `.gitignore`; los logs de `version_N` van en `runs/version_N/tb/`.

`--load` acepta `v16-lucio` (corridas nuevas) o `15` (las viejas, que en disco se llaman `version_15`).

## Corridas y registro

- **Id**: `v<N>-<autor>`. N es global entre los dos autores (el mayor existente + 1). El autor es la
  primera palabra de `git config user.name`. Hacer `git pull` antes de entrenar.
- `train.py --run_id <id>` fija el nombre (hace falta para lanzar varias en paralelo; `tools/run_queue.py` lo usa).
- **Memoria:** cada corrida usa ~3.5 GB de RAM (8 entornos de entrenamiento + 8 de evaluación). En la máquina de
  Lucio (13 GB), no más de 2 corridas a la vez: con 3 se llenó la RAM y se trabó todo.
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
- **Reward**: ver `_computeReward`. Todos los coeficientes son parámetros del entorno (apagados por defecto); las
  variantes con nombre están en `rewards.yaml` y se eligen con `train.py --reward <nombre>`. Para probar una
  recompensa nueva, agregar una variante ahí.
  - **Por defecto (`utils.DEFAULT_REWARD`): `suave_bajada`** desde 2026-10-15: `base` (`−0.1·d − 0.01` por paso,
    +0.1 tocando el tope, +25 − 50·d_xy al aterrizar, −10 al chocar) + `0.02·Σ(a − a_anterior)²` de castigo por
    cambiar la acción + `0.3·(d_xy − 0.25)₊·(velocidad de bajada)₊/0.1` de castigo por bajar estando afuera y a
    menos de 30 cm del tope. 92 % de éxito medio con 4 seeds a 1.5M, contra 54 % de `base`.
  - Con `--load`, se usa la recompensa de esa corrida (`utils.run_reward`; `base` si es vieja y no la tiene).
    Las herramientas que cargan una corrida (`eval.py`, `tools/evaluate.py`, gifs, trayectorias) también.
  - Otros términos: progreso (`reward_progress_coef`, `reward_progress_mode`), PBRS (`reward_pbrs_coef`),
    estar bajo y afuera (`reward_edge_coef`), distancia horizontal y vertical por separado (`reward_dxy_coef`,
    `reward_dz_coef`). Qué dio cada uno: `docs/pruebas-recompensas-2026-10-15.md` y `BITACORA.md`.
  - Ojo: el progreso `k·(d_ant − d)` **no** es shaping por potencial (es PBRS − (1−γ)·k·d), y medirlo sin el
    movimiento de la plataforma (`mode: drone`) se puede explotar persiguiéndola.
- **Las políticas son casi bang-bang**: `dz` saturado en ~97 % de los pasos (bajan siempre a máxima velocidad) y
  la media de la gaussiana muy afuera de [−1, 1]. Ver `tools/action_saturation.py`.

## Convenciones

- Comentarios y mensajes en español.
- La selección del mejor modelo es por tasa de éxito, no por reward (ver el docstring de `BestModelCallback`).
- Con 8 episodios de evaluación, la tasa de éxito va de a 12.5%: no sacar conclusiones de un episodio de diferencia.
- **Para comparar recompensas o hiperparámetros: ≥ 3 seeds por variante, y mirar el modelo final evaluado en
  100 episodios (`eval_final.json`), no solo el best.** Con una sola seed, `base` parecía la mejor y con la seed 1
  no aprende; el best (elegido con 8 episodios) puede estar 20 puntos lejos del final. `tools/compare_runs.py
  --by-reward` junta las seeds. Ver `BITACORA.md`, 2026-10-15.
- **Exploración:** el desvío inicial de la acción (`--log_std_init`, default 0 → desvío 1) pesa tanto como la
  recompensa: con desvío 0.61 (`-0.5`) `base` aprende en todas las seeds. Tenerlo en cuenta al comparar.
- Todo `runs/` se commitea (modelos y TensorBoard), porque es chico y el otro los necesita para evaluar. Los gifs se commitean solo si van al informe.
