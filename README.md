# Aterrizaje de un dron sobre una plataforma móvil

Un Crazyflie (CF2X) aprende con PPO a aterrizar sobre una plataforma con forma de turtlebot que se
mueve y gira. La simulación usa [gym-pybullet-drones](https://github.com/utiasDSL/gym-pybullet-drones)
(PyBullet) y el entrenamiento, [stable-baselines3](https://stable-baselines3.readthedocs.io/). La meta
final es llevar la política a un Crazyflie y un turtlebot reales, con OptiTrack.

## Instalación

```bash
conda create -n drone-landing python=3.12 -y
conda activate drone-landing

# Solo en Linux sin GPU NVIDIA: torch para CPU, mucho más liviano que la versión con CUDA
pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu

pip install -r requirements.txt
```

Si tenés ROS cargado en el `~/.bashrc`, su `PYTHONPATH` se mete en el entorno. Para evitarlo, una sola vez:

```bash
conda env config vars set PYTHONPATH="" -n drone-landing
```

**Todos los comandos se corren desde la raíz del repo**, con el entorno activado. Los scripts de
`tools/` se corren con `python -m tools.<script>`, no con `python tools/<script>.py`.

## Estructura

```
RL-TPFinal/
├── env.py              Entorno de gym: dron, plataforma, observación, recompensa, éxito y choque
├── train.py            Entrenamiento con PPO; guarda todo en runs/<id>/
├── eval.py             Ver una política volar (ventana de PyBullet)
├── utils.py            Rutas de cada corrida, ids, argumentos de línea de comandos, creación del entorno
├── run_registry.py     Escribe runs/<id>/run.json con la config y los resultados de cada corrida
├── levels.yaml         Parámetros del entorno (velocidades de la plataforma, dónde aparece el dron)
├── requirements.txt    Dependencias, con versiones fijas
│
├── runs/               Una carpeta por corrida (ver abajo)
├── tools/              Scripts de análisis
├── media/              gifs/ y plots/ para el informe y la presentación
├── docs/               Consigna, informe y presentación
├── logs/               TensorBoard de las corridas viejas de curriculum (landing_level_1)
│
├── EXPERIMENTS.md      Índice de todas las corridas (generado, no editar a mano)
├── BITACORA.md         Decisiones e ideas, con fecha y autor
├── TODO.md             Pendientes generales, en orden
├── TODO_SIM2REAL.md    Pendientes para pasar al robot real
├── CLAUDE.md           Contexto del proyecto para Claude Code
└── .claude/skills/     Skill /registrar-corrida de Claude Code
```

### `tools/`

| Archivo | Qué hace |
|---|---|
| `evaluate.py` | Evalúa una corrida en muchos episodios sin ventana y guarda `eval_best.json` / `eval_final.json` |
| `generate_gif.py` | Corre un episodio y lo guarda como gif |
| `plot_trajectory.py` | Corre un episodio y grafica la trayectoria del dron y de la plataforma |
| `plots.py` | Grafica curvas de TensorBoard de una o varias corridas (se configura editando su `__main__`) |
| `experiments_index.py` | Regenera `EXPERIMENTS.md` a partir de `runs/*/run.json` |

### `runs/<id>/`: todo lo de una corrida

Las corridas se llaman `v<N>-<autor>` (por ejemplo `v17-lucio`). N es correlativo entre los dos
autores, y el autor sale de `git config user.name`. **Hacer `git pull` antes de entrenar**, para que el
número no se repita.

| Archivo | Qué es |
|---|---|
| `model.zip` | Modelo al final del entrenamiento |
| `best/best_model.zip` | Mejor modelo según las evaluaciones periódicas (tasa de éxito y, si empatan, reward) |
| `run.json` | Argumentos, hiperparámetros, entorno, commit de git, resultados y todas las evaluaciones |
| `diff.patch` | Cambios sin commitear al momento de entrenar (solo si había) |
| `env.py`, `levels.yaml` | Copias exactas de los que se usaron |
| `tb/` | Logs de TensorBoard |
| `eval_best.json` | Evaluación de 100 episodios del best (la escribe `tools/evaluate.py`) |
| `NOTES.md` | Qué cambió respecto de la corrida anterior y qué dio (lo escribe `/registrar-corrida`) |

Si seguís entrenando una corrida con `--load`, los archivos de la sesión nueva llevan sufijo `_s2`, `_s3`, etc.

Las corridas `version_1` a `version_15` y `landing_level_1/2` son anteriores a este registro: solo tienen
el modelo, y no se pueden cargar con el código actual (tenían otra observación y usaban `VecNormalize`).

## Comandos

### Entrenar

```bash
python train.py                                   # corrida nueva, 1M pasos
python train.py --timesteps 5000000               # corrida nueva, 5M pasos
python train.py --load v16-lucio --timesteps 1000000   # seguir entrenando v16-lucio 1M pasos más
```

| Opción | Default | Qué hace |
|---|---|---|
| `--timesteps` | 1 000 000 | Pasos de entrenamiento (de esta sesión, si se usa `--load`) |
| `--n_envs` | 8 | Entornos en paralelo. Conviene no pasar la cantidad de núcleos de la CPU |
| `--seed` | 42 | Semilla. Con la misma semilla y el mismo código, la corrida debería repetirse (salvo diferencias numéricas entre máquinas) |
| `--load` | (ninguno) | Sigue entrenando una corrida existente en vez de crear una nueva |

Cada 100 000 pasos evalúa la política en 8 episodios y guarda el mejor modelo en `best/`. A ~900 pasos
por segundo con 8 entornos, 1M de pasos tarda unos 20 minutos.

Para entrenamientos largos, que siguen aunque cierres la terminal:

```bash
nohup python train.py --timesteps 5000000 > train.log 2>&1 &
tail -f train.log                                 # ver cómo va (Ctrl+C sale del tail, no corta el entrenamiento)
```

### Evaluar en muchos episodios (el número para comparar corridas)

```bash
python -m tools.evaluate --load v17-lucio --best              # best, 100 episodios
python -m tools.evaluate --load v17-lucio --episodes 300      # modelo final, 300 episodios
```

| Opción | Default | Qué hace |
|---|---|---|
| `--load` | la última | Corrida a evaluar |
| `--best` | (apagado) | Evalúa `best/best_model.zip` en vez de `model.zip` |
| `--episodes` | 100 | Cantidad de episodios |
| `--seed` | 42 | Semilla del primer episodio (usa `seed`, `seed+1`, ...). Dejala igual para comparar corridas |

Sin ventana, tarda menos de un minuto para 100 episodios. Imprime la tasa de éxito con su intervalo de
confianza del 95 %, cómo terminan los episodios (éxito, choque contra el piso, contra la plataforma, por
inclinación, o se acaba el tiempo) y cuánto tarda en aterrizar, y lo guarda en `runs/<id>/eval_best.json`
(o `eval_final.json`). Las evaluaciones durante el entrenamiento son de solo 8 episodios y saltan mucho:
para comparar corridas, usar esta.

### Ver una política volar

```bash
python eval.py                                    # la última corrida, 5 episodios
python eval.py --load v16-lucio --episodes 10
```

| Opción | Default | Qué hace |
|---|---|---|
| `--load` | la última | Corrida a cargar: `v16-lucio`, o `15` para las viejas |
| `--episodes` | 5 | Cantidad de episodios |
| `--seed` | 42 | Semilla del entorno (cambiala para ver otros episodios) |

Abre la ventana de PyBullet, corre en tiempo real e imprime cuántos aterrizajes salieron bien.

### Gif de un episodio

```bash
python -m tools.generate_gif --load v16-lucio
python -m tools.generate_gif --load v16-lucio --seed 7 --no-sleep
```

| Opción | Default | Qué hace |
|---|---|---|
| `--load` | la última | Corrida a cargar |
| `--seed` | 42 | Semilla del episodio |
| `--out-dir` | `media/gifs` | Carpeta donde se guarda (`policy_<id>_episode.gif`) |
| `--gif-fps` | 12 | Cuadros por segundo del gif |
| `--capture-every` | 2 | Guarda un cuadro cada N pasos (más chico = gif más fluido y más pesado) |
| `--image-width`, `--image-height` | 640, 480 | Tamaño en píxeles |
| `--no-sleep` | (apagado) | Corre lo más rápido posible en vez de en tiempo real |

### Trayectoria de un episodio

```bash
python -m tools.plot_trajectory --load v16-lucio --out media/plots/trajectory_v16.png
```

Abre la ventana de PyBullet mientras corre el episodio.

| Opción | Default | Qué hace |
|---|---|---|
| `--load` | la última | Corrida a cargar |
| `--seed` | 42 | Semilla del episodio |
| `--out` | `media/plots/trajectory.png` | Dónde se guarda el gráfico |

### Curvas de entrenamiento

```bash
tensorboard --logdir runs                         # todas las corridas; abrir http://localhost:6006
tensorboard --logdir runs/v16-lucio/tb            # una sola
python -m tools.plots                             # gráficos para el informe (editar el __main__ antes)
```

En TensorBoard, lo más útil: `eval/success_rate` (tasa de éxito), `eval/mean_ep_length` (si los episodios
terminan muy rápido, el dron está chocando), `train/explained_variance` (si el crítico aprende, sube hacia 1).

### Índice de experimentos

```bash
python -m tools.experiments_index
```

Regenera `EXPERIMENTS.md`. Si git marca un conflicto en ese archivo, alcanza con correrlo de nuevo.

**Ojo:** `eval.py`, `generate_gif` y `plot_trajectory` cargan el **modelo final** (`model.zip`), no el de `best/`.

## Flujo de trabajo

1. `git pull`.
2. Hacer el cambio (recompensa, entorno, hiperparámetros) y commitearlo, así la corrida queda asociada a
   un commit limpio.
3. `python train.py ...`
4. Ver cómo quedó: `eval.py`, TensorBoard.
5. Evaluar el best: `python -m tools.evaluate --load <id> --best` (si no, lo corre la skill del paso 6).
6. Registrar la corrida con `/registrar-corrida` en Claude Code (escribe `runs/<id>/NOTES.md` y regenera
   `EXPERIMENTS.md`).
7. Commitear `runs/<id>/` y `EXPERIMENTS.md`.

Las decisiones que no son de una sola corrida van en `BITACORA.md`.
