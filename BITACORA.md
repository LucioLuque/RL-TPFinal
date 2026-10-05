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

## 2026-10-04 · lucio · Experimento: sacar el incentivo a chocar para aprender más rápido

En v16/v17 el dron se tiraba al piso al principio (hasta ~0.4M pasos). Con la recompensa `base`, cada paso
cuesta `−0.1·d − 0.01`, y eso se acumula mientras dure el episodio: volar los 480 pasos a ~0.8 m cuesta
≈ −38, y chocar cuesta −10. Mientras no sabe aterrizar, le conviene cortar el episodio chocando.

Variantes en `rewards.yaml`, a comparar contra v17 (seed 42, 1.5M pasos cada una):
- **A1:** progreso `k·(d_anterior − d)` **en vez de** distancia. Sumado en el episodio da `k·(d_inicial −
  d_final)` sin importar la duración, así que chocar ya no conviene. k = 10 da el mismo incentivo de acercarse
  que `0.1·d` acumulado con γ = 0.99 (0.1 / 0.01).
- **A2:** progreso **además** de distancia: más señal de acercarse, pero el costo acumulado sigue.
- **B:** choque a −50, más caro que volar todo el episodio.

Métricas: pasos hasta superar 50 % en `rollout/success_rate`, evaluación de 100 episodios del best y cómo
fallan. Con una sola seed, solo una diferencia grande es señal; si alguna promete, repetirla con más seeds.

Se probó `torch.set_num_threads(1)` para acelerar: no cambió nada (732 contra 750 pasos/s). No se dejó.

## 2026-10-04 · lucio · Resultado: sacar el incentivo a chocar empeoró todo; nos quedamos con `base`

Las tres variantes (seed 42, 1.5M pasos) fueron mucho peores que `base` (v17: 68 % de éxito a 1.5M en el
entrenamiento; 88 % del best en 100 episodios):

| Variante | Éxito a 1.5M | Qué hace |
|---|---|---|
| A1 (v18): progreso en vez de distancia | 0 % | Flota encima de la plataforma y no se anima a bajar |
| A2 (v19): progreso además de distancia | 0 % | Aprende algo a 0.2M (26 % en 100 ep.) y lo pierde |
| B (v20): choque −50 | 0 % | Se queda lejos de la plataforma |

Conclusiones:
- El "chocar rápido" del principio no era el problema: probablemente **ayuda a explorar**. Episodios cortos
  son muchos intentos por millón de pasos, y algunos terminan aterrizando. Sin esa salida (A1, B), el agente
  deja de intentar.
- El progreso con k = 10 no ayudó, aunque en teoría no debería empeorar. A1 es, en teoría, `base` más un
  término de progreso exacto (misma política óptima), y aun así no aprendió: el término cambia cómo aprende,
  no qué es lo óptimo. Además, como la plataforma se mueve, `d` cambia aunque el dron no haga nada, y con
  k = 10 ese ruido es hasta un tercio de la señal.
- Pendiente (`TODO.md`, punto 3): A2 con k chico (0.5, 1, 3) y la suavidad de la acción.

## 2026-10-04 · lucio · Error: el PID del dron no se reiniciaba entre episodios

gym-pybullet-drones no llama a `DSLPIDControl.reset()` en el `reset()` del entorno, así que cada episodio
arrancaba con el error integral y el último ángulo del episodio anterior. El resultado de un episodio
dependía de cuál había corrido antes (se vio porque la seed 52 chocaba en la evaluación y aterrizaba sola).

Se arregló en `env.py` (`reset()` reinicia el PID) y se verificó que la misma seed da lo mismo sola o en
secuencia. Las evaluaciones de 100 episodios se repitieron: casi iguales (v17: 85 % → 88 %; v19: 28 % → 26 %).
**Todas las corridas hasta v20 se entrenaron con el error**: las próximas no son exactamente comparables,
así que conviene entrenar una `base` nueva como referencia.

Con el error arreglado, los fallos de v17 son claros: 11 de 12 son choques contra el borde. Medio segundo
antes, el dron está afuera de la plataforma (0.28–0.43 m del centro; radio 0.25) y bajo (10–18 cm sobre el
tope), bajando en diagonal. Hipótesis: `−0.1·d` se achica igual bajando que acercándose en horizontal, así
que bajar en diagonal le conviene. Próxima prueba: pesar más la distancia horizontal que la vertical.

## 2026-10-04 · lucio · Base con el PID arreglado (v21) y variante XY (v22)

Las dos con seed 42 y 1.5M pasos, con el PID arreglado.

- **v21 (`base`):** la curva de éxito es casi igual a la de v17 (72 % contra 68 % a 1.5M), así que el
  error del PID no cambiaba el aprendizaje. Best (0.9M): 65 % en 100 episodios. Los 31 choques contra la
  plataforma tienen el mismo patrón que en v17 (bajar en diagonal desde afuera): es el modo de fallo de
  `base`. Queda como referencia para las variantes de 1.5M pasos.
- **v22 (`XY`: `−0.1·d_xy − 0.033·|dz|`):** el dron aprendió a alinearse arriba de la plataforma y los
  choques contra el borde bajaron (10 contra 31), pero no baja: 48 de 100 episodios terminan por tiempo,
  flotando a ~20 cm sobre el centro. Aprende mucho más lento (4 % de éxito en el entrenamiento a 1.5M
  contra 72 %; best 35 % en 100 episodios) y tarda más en aterrizar (10.5 s contra 2.4 s).

Se repite lo de A1 (v18): cuando la recompensa deja de empujar a terminar el episodio, el agente prefiere
flotar. Sigue pendiente cómo atacar los choques contra el borde.
