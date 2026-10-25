# TODO

Pendientes del proyecto, en orden. **Solo lo que falta:** cuando algo se termina, se borra de acá (queda registrado en
`BITACORA.md`, `EXPERIMENTS.md`, las `NOTES.md` de cada corrida y git). Lo de pasar al robot real está en `SIM2REAL.md`,
en `~/Documents/Tesis/Laboratorio`.

## 1. Elegir la recompensa y la exploración finales

Las candidatas, con desvío inicial 0.61 (`--log_std_init -0.5`): `suave_bajada_c003` (castigo a la acción 0.03: 97.7 %
con 3 seeds a 1.5M) y `suave_bajada_c005` (0.05: la más suave, pero con 1.5M pasos la mitad de las seeds aprende tarde;
a 3M llegan a 100 %). Detalle en `BITACORA.md`, 2026-10-25.

- [ ] Entrenar las dos a 3M completo con 3 seeds (`cola_pendiente.txt`). Repiten completas v103 y v104, que se cortaron
  antes del final y solo tienen el best.
- [ ] **Decidir (Lucio)** si cambian `DEFAULT_REWARD` (`utils.py`) y el default de `log_std_init` (`train.py`). Hoy siguen
  `suave_bajada` y 0.
- [ ] Corriendo (`cola_huecos.txt`): seeds 1 y 2 de `PBRS_k10` (v43, v48) y de `A2_k1` (v44, v49). Registrar, sacar de
  acá y borrar `cola_huecos.txt` cuando terminen.

## 2. Ideas sin probar

- [ ] **Centrar mejor:** el premio terminal al centro no sirve (`suave_bajada_centro`); probar algo que actúe antes de
  tocar, sin encarecer bajar (trampa de flotar). Entrenar más pasos sí centra (v69, v100).
- [ ] **Acción no bang-bang:** las políticas saturan `dz` en ~97 % de los pasos. Probar la acción como velocidad directa
  (`v = 0.6·a`, sin normalizar la dirección) o con `tanh` en el entorno. Cambia la acción: después de medir en el
  laboratorio, en corrida aparte, y revisar `SIM2REAL.md`.
- [ ] **Desvío inicial 0.37 con las recompensas candidatas:** con `base`, bajar el desvío de 0.61 a 0.37 subió el éxito
  de 79 a 85 % (3 seeds, v60–v62), aprendiendo más tarde. Probarlo con `suave_bajada_c003`.
- [ ] **Yaw en la observación:** normalizado por π tiene un salto en ±π y casi no influye (la acción está en el marco del
  mundo). Sacarlo o reemplazarlo por sin/cos, en corrida aparte.

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
