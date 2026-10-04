# v16-lucio

Cambio: normalización fija (sin VecNormalize), dron a 0.6 m/s y contacto base-tope

Primera corrida con registro. No hay una anterior con `run.json`: se compara contra el código de
`f94b2d3` (el último antes del registro), que es el que usaban las corridas `version_N`. De esas
corridas no hay resultados registrados.

| | antes (`f94b2d3`) | v16-lucio |
|---|---|---|
| Éxito best (100 ep.) | sin registro | 4% (2–10) |
| Best éxito (8 ep.) | sin registro | 0% |
| Best reward | sin registro | −9.16 |
| Largo ep. (best) | sin registro | 103 pasos |
| Best en timestep | sin registro | 200 000 |
| Timesteps totales | sin registro | 200 704 (3.7 min, 8 entornos) |

## Qué cambió
- **Observación:** normalizada con escalas fijas a [-1, 1] (`_obs_scale`) en vez de `VecNormalize`.
  Mismas 19 dimensiones y mismo orden.
- **Recompensa:** sin normalizar (antes `VecNormalize` la dividía por ~4). Los términos de
  `_computeReward` no cambiaron.
- **Velocidad máxima del dron:** 0.25 → 0.6 m/s (`DRONE_SPEED_LIMIT`). Cambia el significado de la acción.
- **Contacto:** `top` solo si es la base del dron contra el tope (normal hacia arriba). Antes alcanzaba con
  ±5 cm de la altura del tope, y un golpe en el costado cerca del borde contaba como `top`.
- **Librería:** gym-pybullet-drones 2.1.0 → 2.2.0. No cambia la simulación.
- Hiperparámetros, entorno (`turtlebot_hard_fixed`) y seed (42): iguales.

## Por qué
Ver `BITACORA.md` (2026-10-03 y 2026-10-04). La normalización fija la sugirió el profe (`VecNormalize`
no conviene con rangos conocidos, y la misma cuenta sirve para el robot real). La velocidad, porque con
0.25 m/s el dron no podía alcanzar una plataforma que va a hasta 0.3 m/s. El contacto, para no premiar
golpes contra el costado. Esta corrida era sobre todo una prueba corta de que el registro y estos cambios
funcionan de punta a punta.

## Resultado
**Datos.** Solo hubo 2 evaluaciones (100k y 200k pasos): éxito 0% en ambas; reward −18.9 → −9.2 y largo
de episodio ~102 → ~103 pasos (de 480). El crítico aprende bien sin escalar la recompensa
(`explained_variance` 0.77 y `value_loss` 0.2 al final). La política todavía explora mucho (`std` 1.1).

Evaluación con `tools/evaluate.py` (100 episodios, seeds 42–141): 4 % de éxito (IC 95 %: 2–10 %); 80 choques
contra el piso, 12 contra la plataforma y 4 por inclinación.

Evaluación anterior, hecha a mano (20 episodios deterministas, seeds 1000–1019):
- 19 choques y 1 aterrizaje (5%).
- Los choques son **contra el piso**: altura final ~1.4 cm (el dron apoyado en el suelo), a una distancia
  horizontal mediana de 0.71 m de la plataforma, después de una mediana de 41 pasos (1.7 s). El dron
  baja casi derecho y nivelado (roll y pitch < 0.1 en la mayoría).
- **Normalización:** solo se recorta la velocidad angular en x e y (0.6 % y 1.2 % de los pasos; el criterio
  era < 1 %). Percentil 99.9: ~9 y 7 rad/s, contra la escala de 5. Posición (p99.9 ~1.2 m contra 1.5) y
  velocidades (p99.9 ≤ 0.7 m/s contra 0.75 y 1.125): bien.

**Hipótesis: tirarse al piso le conviene al principio.** Con la recompensa actual, cada paso cuesta
−0.01 − 0.1·d. A ~0.8 m, son unos −0.09 por paso. Chocar a los 41 pasos suma −3.7 − 10 ≈ −14, y mantenerse
en el aire los 480 pasos sin aterrizar suma ≈ −43. Mientras no sepa aterrizar, chocar rápido le conviene
más que seguir volando. **Pero probablemente solo retrasa el aprendizaje:** las corridas viejas
(`media/plots/version_logs_rollout_success_rate_v1_8_13.png`) estuvieron cerca de 0 % hasta 1–2.2 M pasos
y después llegaron a ~95 %. Con 200k pasos, esta corrida cortó mucho antes de ese punto, así que no dice si
la configuración nueva aprende.

## Próximo paso
1. Corrida larga (5M pasos) con la misma configuración, para ver si el éxito despega como en las viejas.
   Si a los 5M sigue en ~0 %, recién ahí cambiar la recompensa (por ejemplo, que chocar cueste más de lo
   que se puede acumular volando).
2. Subir `OBS_ANG_VEL_SCALE` a ~10 rad/s, pero recién con una política que no choque tanto: ahora los
   picos de velocidad angular pueden venir de los choques.
