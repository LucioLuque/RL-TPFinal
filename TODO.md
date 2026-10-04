# TODO

Pendientes generales del proyecto, en orden. Los de pasar al robot real están en `TODO_SIM2REAL.md`.

## 1. Reemplazar VecNormalize por una normalización fija

**Por qué:** `VecNormalize` normaliza con una media y un desvío que va estimando
durante el entrenamiento. Eso sirve cuando no se conoce la distribución de los valores, pero acá la
mayoría tiene un rango conocido por la física o por las reglas del entorno. Si se sabe el rango, es
mejor normalizar con eso. Además:
- **Sim2real:** con una normalización fija, la misma cuenta se aplica igual en simulación y con
  OptiTrack. Con `VecNormalize`, en el robot real habría que usar estadísticas estimadas en la
  simulación, guardadas en un `.pkl`.
- **Estabilidad:** con `VecNormalize`, la normalización cambia mientras la política aprende, así que la
  misma observación significa otra cosa al principio y al final del entrenamiento.
- **Simplicidad:** desaparecen `vecnormalize.pkl`, el callback que lo guarda junto al best, la
  sincronización con el entorno de evaluación y la normalización a mano en `tools/generate_gif.py`.

**Cómo:** en `_computeObs`, dividir cada valor por su escala y recortar a [-1, 1]. El
`observation_space` pasa a ser `Box(-1, 1)` en vez de infinito.

**Valores propuestos.** La columna "σ en v10" es el desvío que estimó `VecNormalize` en la versión 10
(con el límite viejo de 0.25 m/s); sirve para verificar que las escalas tengan sentido, no para elegirlas.

| Valor | Dims | Escala | Por qué ese valor | σ en v10 |
|---|---|---|---|---|
| Posición relativa xy | 2 | 1.5 m | El dron aparece a ≤ 0.8 m de la plataforma (`spawn_xy_radius`); con margen para que se aleje. Más lejos de 1.5 m ya está perdido, así que recortar ahí no pierde información útil (se mantiene el signo). | 0.44, 0.40 |
| Posición relativa z | 1 | 1.5 m | Aparece a una altura de 0.5–1.5 m (`spawn_z_range`), y el tope de la plataforma está a 0.35 m. | 0.27 |
| Velocidad relativa | 3 | 1.125 m/s | Peor caso, en sentidos opuestos: dron (≤ 0.6, `DRONE_SPEED_LIMIT`) + plataforma (≤ 0.3) = 0.9, × 1.25 de margen (`VEL_MARGIN`). | 0.15, 0.15, 0.09 |
| Roll, pitch | 2 | 0.7 rad | A más de 0.7 rad el episodio termina como choque (`_crashed`), así que nunca se pasa. | 0.08, 0.08 |
| Yaw | 1 | π | Está en [-π, π]. Ver la nota de abajo. | 0.48 |
| Velocidad angular | 3 | 5 rad/s | **No tiene un límite conocido.** Es el único valor elegido mirando datos: σ ≈ 1.2, así que 5 rad/s cubre más de 4σ. | 1.27, 1.26, 1.05 |
| Velocidad del dron | 3 | 0.75 m/s | Límite de 0.6 m/s más un 25 % de margen para el sobrepaso del controlador y las caídas. | 0.14, 0.15, 0.09 |
| Acción previa | 4 | no se toca | Ya está en [-1, 1] (dirección) y [0, 1] (`s`). | |

Si se cambia `DRONE_SPEED_LIMIT` o los rangos de la plataforma, hay que recalcular la velocidad relativa
y la del dron. Lo mejor es calcular las escalas a partir de esas constantes, no escribirlas a mano.

**Nota sobre el yaw:** como la acción es una velocidad en el marco del mundo, el yaw casi no influye en la
tarea. En v10 tiene σ ≈ 0.48, así que el dron gira sin control. Normalizarlo por π tiene un salto en
±π. Opciones a futuro: sacarlo de la observación, o reemplazarlo por sin/cos. Ese cambio va en una
corrida aparte, no en esta.

**Recompensa:** hoy `VecNormalize` también normaliza la recompensa (`norm_reward=True`). La escala es
conocida: hasta unos −0.1 por paso, +25 al aterrizar y −10 al chocar. Así que la normalización también
se saca. Si la pérdida del crítico (`train/value_loss`) queda muy alta, multiplicar la recompensa por
una constante fija.

**Cómo validar:**
- Medir qué fracción de cada valor queda recortada en ±1. Debería ser menor al 1 %; si no, la escala
  está chica.
- Comparar la curva de éxito contra una corrida con `VecNormalize` y el mismo `env.py` (mismo límite de
  velocidad). Si no, no se sabe qué cambio causó la diferencia.

**Qué hay que tocar:**
- [x] `env.py`: escalas como constantes derivadas de los límites, normalizar en `_computeObs` y
  `observation_space` en [-1, 1].
- [x] `train.py`: sacar `VecNormalize`, `SaveVecNormalizeCallback` y `sync_envs_normalization`.
- [x] `eval.py` y `tools/`: cargar solo el modelo.
- [x] `utils.py` y `run_registry.py`: sacar las rutas de `vecnormalize.pkl`; guardar las escalas en
  `run.json`.
- [x] `CLAUDE.md`: actualizar lo de la observación y los archivos de cada corrida.
- [x] Anotar el cambio en `BITACORA.md`.
- [ ] Registrar la corrida con `/registrar-corrida` y medir la fracción recortada de cada valor.
- [ ] Ajustar `OBS_ANG_VEL_SCALE` (provisoria, sale de v10) con el percentil 99.9 de la corrida.

## 2. Corrida de prueba y primer commit del registro

- [ ] Entrenar una corrida corta y verificar que `runs/<id>/` queda completo (modelo, best, `run.json`,
  `diff.patch`, `tb/`).
- [ ] Correr `/registrar-corrida` y revisar `NOTES.md` y `EXPERIMENTS.md`.

## 3. Comparar términos de la recompensa

Las variantes se definen con nombre en `rewards.yaml` y se entrenan con `train.py --reward <nombre>`.

**Ya probado (2026-10-04, seed 42, 1.5M pasos; ver `runs/v18`–`v20` y `BITACORA.md`):**

| Variante | Qué cambia respecto de `base` | Éxito a 1.5M (v17/`base`: 68 %) |
|---|---|---|
| A1 (v18) | progreso `10·(d_anterior − d)` **en vez de** `−0.1·d` | 0 % (flota encima, no baja) |
| A2 (v19) | progreso `10·(d_anterior − d)` **además de** `−0.1·d` | 0 % (aprendió algo a 0.2M y lo perdió) |
| B (v20) | choque −50 en vez de −10 | 0 % (se queda lejos) |

Con k = 10, el progreso domina la recompensa por paso (hasta ±0.37, contra ~0.08 del resto) y mete ruido,
porque la plataforma se mueve y cambia `d` aunque el dron no haga nada.

**Pendiente:**
- [ ] **A2 con factores más chicos:** progreso sumado a `base` con k = 0.5, 1 y 3 (agregar `A2_k05`, `A2_k1`,
  `A2_k3` a `rewards.yaml`). Con k chico, la señal de acercarse ayuda sin dominar ni meter tanto ruido.
- [ ] **Suavidad de la acción:** `base` + `−c·sum((acción − acción_previa)²)`. Hay que agregar
  `reward_action_coef` como parámetro del entorno (hoy está comentado en `_computeReward`). Probar c = 0.02.
  Medir también cuánto cambia la acción entre pasos, en `base` y en esta variante.
- Mismos timesteps (1.5M) y seed (42) que v18–v20, para comparar contra la curva de v17. Si alguna
  promete, repetirla con más seeds.

## 4. ❓ Marco de referencia de la observación y la acción: ¿hace falta probar el de la plataforma?

**Pregunta abierta** (consultar con el profesor): ¿tiene sentido que la acción esté en el marco del
mundo? Antes de decidir, hay que definir si esta prueba hace falta.

**Hoy está todo en el marco del mundo** (verificado en `env.py` y en gym-pybullet-drones: el estado sale
de `getBaseVelocity` y `getBasePositionAndOrientation` de PyBullet, que devuelven todo en coordenadas
del mundo). Contra lo que se suponía, la observación **no** está en el marco del robot:

| | Valor | Marco | Detalle |
|---|---|---|---|
| Obs | Posición relativa | Mundo, con origen en el tope de la plataforma | `drone_pos - platform_top`: se resta el origen, pero los ejes no se rotan |
| Obs | Velocidad relativa | Mundo | `drone_vel - platform_vel` |
| Obs | Roll, pitch, yaw | Orientación del dron respecto del mundo | Ángulos de Euler |
| Obs | Velocidad angular | Mundo | No en el marco del dron (un IMU la daría en el marco del dron) |
| Obs | Velocidad del dron | Mundo | |
| Obs | Acción previa | Mundo | |
| Acción | `[dx, dy, dz]` y `s` | Mundo | El controlador PID compara la velocidad pedida con la actual, ambas en el mundo |

La observación y la acción ya son coherentes entre sí. Además, la observación no incluye hacia dónde
apunta la plataforma ni cuánto gira.

**Opciones:**
- **Marco del mundo (hoy):** la tarea es igual en cualquier dirección, porque la plataforma arranca
  orientada al azar. La red tiene que aprender lo mismo para cada dirección. Funciona, pero desperdicia datos.
- **Marco de la plataforma:** rotar la posición y la velocidad relativas según el yaw de la
  plataforma, y rotar la acción de vuelta al mundo antes de mandarla. Así la plataforma siempre
  "avanza hacia +x", el agente aprende un solo caso, y la dirección del movimiento queda implícita en
  la observación. En el robot real, OptiTrack da el yaw del turtlebot.
- **Marco del dron:** no recomendado. El yaw del dron no se controla y deriva (σ ≈ 0.48 en v10), así
  que la acción cambiaría de significado a medida que el dron gira.

**Si se prueba:** en una corrida aparte, después del punto 1, comparada contra la misma configuración
en el marco del mundo.

- [ ] Decidir si hace falta la prueba (consultar con el profesor).
- [ ] Si hace falta: implementarla como opción del entorno, entrenar y anotar la conclusión en `BITACORA.md`.

## 5. Evaluar el best, no solo el modelo final

`eval.py`, `tools/generate_gif.py` y `tools/plot_trajectory.py` cargan siempre `model.zip`. El mejor
checkpoint (`best/best_model.zip`) solo se puede usar a mano.

- [ ] Agregar `--best` a esos scripts.

## 6. Sim2real

- [ ] Resolver lo de `TODO_SIM2REAL.md`.
