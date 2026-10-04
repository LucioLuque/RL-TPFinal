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
