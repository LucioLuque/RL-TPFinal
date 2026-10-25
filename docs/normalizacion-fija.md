# Normalización fija de la observación (2026-10-04)

Por qué se reemplazó `VecNormalize` por escalas fijas y de dónde sale cada escala. Estaba en `TODO.md`, punto 1, hasta que se terminó (2026-10-25); la decisión está en `BITACORA.md`, 2026-10-04. Las escalas están en `env.py` (constantes `OBS_*` y `_obs_scale`).

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
