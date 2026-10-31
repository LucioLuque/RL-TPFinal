# TODO

Pendientes del proyecto, en orden. **Solo lo que falta:** cuando algo se termina, se borra de acá (queda registrado en
`BITACORA.md`, `EXPERIMENTS.md`, las `NOTES.md` de cada corrida y git). Lo de pasar al robot real está en `SIM2REAL.md`,
en `~/Documents/Tesis/Laboratorio`.

## 1. Elegir la recompensa y la exploración finales

A 3M pasos con desvío inicial 0.61 (`--log_std_init -0.5`): `suave_bajada_c003` da 100 % con 3 seeds (v105–v107);
`suave_bajada_c005` es más suave, pero 1 de 5 seeds se quedó flotando (v109); y `suave_bajada` también da 100 % con 3
seeds (v130–v132), algo menos suave que `c003`. Con desvío 0.37, `c003` centra mejor y aprende ~0.5M pasos más tarde
(v133–v135). Detalle en `BITACORA.md`, 2026-10-30.

- [ ] **Decidir (Lucio)** si cambian `DEFAULT_REWARD` (`utils.py`), el default de `log_std_init` y el de `--timesteps`
  (`DEFAULT_TOTAL_TIMESTEPS`, `train.py`). Hoy son `suave_bajada`, 0 y 1M. La recomendación de la noche del 2026-10-30: `c003`, desvío 0.61
  y 3M.

## 2. Ideas sin probar

- [ ] **Tocar suave, siguiente paso:** con la acción como velocidad y el premio por tocar despacio
  (`suave_bajada_c003_vel_tocar`), v127 toca a 0.33 m/s, pero las otras 2 seeds no frenan (`BITACORA.md`, 2026-10-30).
  Probar, en este orden: curriculum desde v127 con más premio (`train.py --init_from v127-teo` con `landing_vz_coef` 25,
  una variante nueva en `rewards.yaml`), el mismo premio de 25 desde cero con 3 seeds, y combinarlo con el castigo a
  salirse de [−1, 1] (ítem siguiente). La acción como velocidad cambia la interfaz con el dron: revisar `SIM2REAL.md`
  antes de elegirla.
- [ ] **Castigar que la media de la gaussiana se salga de [−1, 1]** (*bounds loss*, como `bounds_loss_coef` de
  rl_games): hoy las medias están en ~1.5–3 (`tools/action_saturation.py`), así que la exploración casi nunca prueba
  valores intermedios y la acción sale bang-bang. Va en la pérdida de PPO, como CAPS (`caps.py`), no en la recompensa.
- [ ] **Combinar lo que centra:** CAPS (v121–v123: 2.7–3.8 cm), gSDE (v118–v120) y el desvío 0.37 (v133–v135) centran
  mejor que `c003` solo, cada uno por separado. Probar `c003` + desvío 0.37 + CAPS o gSDE.
- [ ] **Yaw en la observación:** normalizado por π tiene un salto en ±π y casi no influye (la acción está en el marco del
  mundo). Sacarlo o reemplazarlo por sin/cos, en corrida aparte.
- [ ] **Más suavidad con curriculum:** entrenar a aterrizar y después seguir con más castigo a la acción (0.05, 0.1),
  que desde cero deja al dron flotando: `train.py --init_from <run> --reward <otra>`. Kooi y Babuška (2021) y
  Goldschmid y Ahmad (2024) usan curriculum (`docs/estado-del-arte-2026-10-30.md`).
- [ ] **Perfil de bajada (teoría tau):** referencia `v_ref(h)` que frena con τ̇ constante (τ = h / v_bajada). Usarla
  con curriculum, no desde el principio (trampa de flotar).
- [ ] **Controlador híbrido para el tramo final:** RL para alinearse y una ley fija (`vz = −k·h` con un mínimo) en los
  últimos centímetros. Cambia la acción: revisar `SIM2REAL.md`.
- [ ] **Suavidad sin recompensa, otras variantes:** CAPS con 0.01 y gSDE suavizaron solo ~12–15 % (`BITACORA.md`,
  2026-10-30). Probar CAPS sobre la media recortada a [−1, 1] o con más peso (0.05–0.1), gSDE con `--sde_sample_freq`
  8 o 16, Lipschitz-Constrained Policies (Chen et al. 2024) y ruido coloreado en PPO.

## 3. Ajustar la escala de la velocidad angular

`OBS_ANG_VEL_SCALE` (5 rad/s, `env.py`) es provisoria (sale de v10). En las políticas actuales `wx` y `wy` se recortan
en ~1.1 % de los pasos (`obs_clipped_fraction` en `eval_final.json`), justo arriba del 1 % que se pedía. Ajustarla con
el percentil 99.9 (`obs_abs_p999`) de las mejores corridas. Cambia la observación: corrida aparte.

## 4. ❓ Marco de referencia de la observación y la acción: ¿hace falta probar el de la plataforma?

**Pregunta abierta** (consultar con el profesor): ¿tiene sentido que la acción esté en el marco del mundo?

**Hoy está todo en el marco del mundo** (verificado en `env.py` y en gym-pybullet-drones: el estado sale de
`getBaseVelocity` y `getBasePositionAndOrientation` de PyBullet, que devuelven todo en coordenadas del mundo). La
observación **no** está en el marco del robot:

| | Valor | Marco | Detalle |
|---|---|---|---|
| Obs | Posición relativa | Mundo, con origen en el tope de la plataforma | `drone_pos - platform_top`: se resta el origen, pero los ejes no se rotan |
| Obs | Velocidad relativa | Mundo | `drone_vel - platform_vel` |
| Obs | Roll, pitch, yaw | Orientación del dron respecto del mundo | Ángulos de Euler |
| Obs | Velocidad angular | Mundo | No en el marco del dron (un IMU la daría en el marco del dron) |
| Obs | Velocidad del dron | Mundo | |
| Obs | Acción previa | Mundo | |
| Acción | `[dx, dy, dz]` y `s` | Mundo | El controlador PID compara la velocidad pedida con la actual, ambas en el mundo |

La observación y la acción son coherentes entre sí. La observación no incluye hacia dónde apunta la plataforma ni cuánto
gira.

**Opciones:**
- **Marco del mundo (hoy):** la tarea es igual en cualquier dirección, porque la plataforma arranca orientada al azar.
  La red tiene que aprender lo mismo para cada dirección. Funciona, pero desperdicia datos.
- **Marco de la plataforma:** rotar la posición y la velocidad relativas según el yaw de la plataforma, y rotar la
  acción de vuelta al mundo antes de mandarla. Así la plataforma siempre "avanza hacia +x", el agente aprende un solo
  caso, y la dirección del movimiento queda implícita en la observación. En el robot real, OptiTrack da el yaw del
  turtlebot.
- **Marco del dron:** no recomendado. El yaw del dron no se controla y deriva, así que la acción cambiaría de
  significado a medida que el dron gira.

- [ ] Decidir si hace falta la prueba (consultar con el profesor).
- [ ] Si hace falta: implementarla como opción del entorno, entrenar y anotar la conclusión en `BITACORA.md`.

## 5. Evaluar el best, no solo el modelo final

`eval.py`, `tools/generate_gif.py` y `tools/plot_trajectory.py` cargan siempre `model.zip`. El mejor checkpoint
(`best/best_model.zip`) solo se puede usar a mano (hoy, por ejemplo, v103 y v104 no se pueden mirar con `eval.py`).

- [ ] Agregar `--best` a esos scripts.

## 6. Sim2real

- [ ] Resolver lo de `SIM2REAL.md` (`~/Documents/Tesis/Laboratorio`; ahí también está la guía del laboratorio).

## 7. Efecto suelo y otras variables reales que faltan en la simulación

Detalle y fuentes en `docs/estado-del-arte-2026-10-30.md`. Revisar contra `SIM2REAL.md` antes de implementar: puede
que algo ya esté ahí.

- [ ] **Medir el efecto suelo en el laboratorio:** hover a 2, 4, 6, 10 y 20 cm sobre el tope del turtlebot quieto,
  registrar el empuje del log del firmware y ajustar `ground_effect_scale` (`env.py`). El modelo de gym-pybullet-drones
  da ~18 % a 4.6 cm; mediciones en un Crazyflie 2.0 dan ~5 %.
- [ ] **Aleatorizar `ground_effect_scale`** por episodio (por ejemplo entre 0 y 1.5) mientras no esté medido.
- [ ] **Latencia:** retardo de 0–2 pasos en la acción, sorteado por episodio (OptiTrack → PC → radio → Crazyflie).
- [ ] **Masa e inercia:** aleatorizar ±20 % (marcadores de OptiTrack, batería; Molchanov et al. 2019).
- [ ] **Batería:** aleatorizar el empuje máximo (`KF`) ±10 %.
- [ ] **Drag y downwash:** probar `Physics.PYB_GND_DRAG_DW` con el efecto suelo contra el tope.
- [ ] **Ruido en la observación** (velocidad derivada de OptiTrack), **rebote y fricción del tope**, y **corrientes de
  aire** (fuerza chica constante por episodio).
