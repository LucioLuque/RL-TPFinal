# Bitácora

Ideas, decisiones y observaciones del proyecto que no son de una sola corrida (lo de cada corrida va
en `runs/<id>/NOTES.md`). Entradas nuevas al final, con fecha y autor. Si hay conflicto de merge,
quedarse con las entradas de los dos.

Formato:

```markdown
## 2026-10-03 · lucio · <título corto>
<qué se observó, decidió o se quiere probar, y por qué. Mencionar corridas relacionadas (v16-lucio).>
```

---

## 2026-10-03 · lucio · Límite de velocidad del dron: 0.25 → 0.6 m/s

`VelocityAviary` limita la velocidad que se le pide al dron a `0.03 × 30 km/h = 0.25 m/s`. La
plataforma se sortea entre 0.05 y 0.3 m/s (y el sorteo favorece las velocidades altas), así que en
los episodios en que va casi recta el dron no podía alcanzarla. Probablemente eso limitaba la tasa
de éxito de todas las corridas anteriores.

Se sube a 0.6 m/s (`DRONE_SPEED_LIMIT` en `env.py`): alrededor del doble de la velocidad máxima de la
plataforma, para que el dron pueda alcanzarla e igualarle la velocidad, sin ser tan alto que
aterrizar con precisión se vuelva más difícil o que sea inseguro en el volumen de OptiTrack.

Cambia lo que significa la acción (mismo `s`, otra velocidad), así que los modelos anteriores no son
comparables directamente y hay que reentrenar.

**Hay que validarlo en el robot real:** el firmware del Crazyflie, en modo velocidad, no tiene tope de
velocidad (limita la inclinación a 20°). El límite de 0.6 m/s lo tiene que aplicar el código que manda
los comandos, con la misma fórmula que la simulación. Ver `TODO_SIM2REAL.md`, punto 4.

## 2026-10-04 · lucio · Normalización fija en vez de VecNormalize

Lo sugirió el profe: `VecNormalize` no conviene cuando la distribución es conocida; si se sabe el rango,
normalizar con eso. Ahora `env.py` divide cada valor de la observación por una escala fija y recorta a
[-1, 1]. Las escalas salen de límites del entorno (aparición, choque, límites de velocidad, con 25 % de
margen), salvo la de la velocidad angular, que es provisoria y sale de datos de v10. Detalle y motivo de
cada valor en `TODO.md`, punto 1.

Ventajas: la misma cuenta sirve para el robot real (sin `.pkl` de estadísticas de simulación), la
normalización no cambia mientras la política aprende, y el código es más simple.

La recompensa queda **sin normalizar** por ahora (antes `VecNormalize` la dividía por ~4). Si
`train/value_loss` sale muy alta o `train/explained_variance` no sube, probar un factor fijo
(por ejemplo, 0.1) en `make_env`, después del `Monitor`.

Con acciones al azar, la posición se recorta seguido (11 % en x) porque el agente se aleja; el
número que importa es el de una política entrenada.

## 2026-10-04 · lucio · Contacto con la plataforma: base del dron contra el tope

Antes, un contacto contaba como "tocar el tope" si el punto estaba a ±5 cm de la altura del tope. Un
golpe contra el costado de la plataforma, cerca del borde, entraba en ese margen y cobraba el +0.1 por
tocar (comprobado en simulación: punto a 0.331 m → `top`).

Ahora `top` exige que la superficie tocada de la plataforma mire hacia arriba (normal z > 0.9) y que el
punto esté en la cara de abajo del dron. Cualquier otro contacto es choque.

Se evaluó contar el contacto por las 4 patas, pero el modelo CF2X no tiene patas (la colisión es un
cilindro de 12 cm × 2.5 cm) y PyBullet da 1 o 2 puntos de contacto, no 4. Hacerlo requeriría un URDF
propio con patas: se descartó por ahora. Este criterio no distingue apoyado plano de inclinado sobre el
borde de la base; eso lo cubre la condición de aterrizaje (roll y pitch < 0.1).
