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
los comandos, con la misma fórmula que la simulación. Ver `TODO_SIM2REAL.md`, punto 4 (desde el 2026-10-25, `SIM2REAL.md` en `~/Documents/Tesis/Laboratorio`).

## 2026-10-04 · lucio · Normalización fija en vez de VecNormalize

Lo sugirió el profe: `VecNormalize` no conviene cuando la distribución es conocida; si se sabe el rango,
normalizar con eso. Ahora `env.py` divide cada valor de la observación por una escala fija y recorta a
[-1, 1]. Las escalas salen de límites del entorno (aparición, choque, límites de velocidad, con 25 % de
margen), salvo la de la velocidad angular, que es provisoria y sale de datos de v10. Detalle y motivo de
cada valor en `docs/normalizacion-fija.md` (antes `TODO.md`, punto 1).

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

## 2026-10-15 · lucio · El progreso k·(d_ant − d) no es shaping por potencial

El shaping por potencial (Ng et al. 1999) con `Φ = −k·d` es `γ·Φ(s') − Φ(s) = k·(d_ant − d) + (1−γ)·k·d`. O sea,
el progreso que usaban A1 y A2 es **PBRS − (1−γ)·k·d**; con k = 10 y γ = 0.99, **PBRS − 0.1·d**. Consecuencias:
A2 (v19) era `base` con el **doble** de castigo por distancia más PBRS, no "base más una ayuda"; y A1 (v18) tiene casi
la misma política óptima que `base` (difiere solo en el paso terminal), así que no aprendió por cómo aprende, no por
qué es óptimo. El PBRS bien hecho está en `env.py` (`reward_pbrs_coef`).

Otro detalle: el "ruido" que mete el movimiento de la plataforma en el progreso no hay que sacarlo. Midiendo el
progreso solo con lo que se movió el dron (v27, `A2_k3_drone`) deja de ser telescópico, y el agente aprende a
perseguir la plataforma a distancia fija cobrando progreso sin acercarse (+16 por episodio contra 0). Con k chico
(1–3), el progreso normal funciona: aprende en todas las seeds, a veces antes que `base`, pero no sube el techo.
Detalle en `docs/pruebas-recompensas-2026-10-15.md`.

## 2026-10-15 · lucio · Comparar recompensas con una sola seed engaña

`base` con la seed 1 (v29) no aprende nada: queda flotando, igual que A1, B y XY. Con las seeds 2, 3 y 42 sí aprende
(70–76 %). Todas las comparaciones anteriores eran con la seed 42, que para `base` resultó ser buena; los fracasos
de v18, v20 y v22 no prueban que esas recompensas sean malas.

Además, el best que guarda `train.py` se elige con 8 episodios y es muy ruidoso: v21 tiene best 65 % y final 72 %;
v57, best 75 % y final 93 %.

**Desde ahora:** comparar recompensas con ≥ 3 seeds, y con el **modelo final** evaluado en 100 episodios
(`python -m tools.evaluate --load <id>` → `eval_final.json`), además del best. `tools/compare_runs.py --by-reward`
junta las seeds de cada recompensa. `EXPERIMENTS.md` ahora muestra el éxito final.

## 2026-10-15 · lucio · El ruido de exploración pesa más que los pesos de la recompensa

La política arranca con desvío 1 (`log_std_init = 0`) sobre acciones en [−1, 1]: la mitad de las acciones
muestreadas cae afuera del rango y se recorta. Con tanto ruido, casi todos los intentos de bajar terminan en choque,
y cualquier término que encarezca bajar (XY, B, A1, `borde_k1`) lleva al agente a flotar.

- El castigo `0.02·Σ(Δa)²` (`suave_c002`) baja ese ruido (`train/std` 0.89 contra 1.10 a 0.25M) y aprende en
  4 de 4 seeds (74 %), antes que `base`, cambiando la acción ~3 veces menos.
- Control sin tocar la recompensa: `base` con `--log_std_init -0.5` (desvío 0.61) aprende en 3 de 3 seeds (79 %).
- Las dos cosas se suman: `suave_c002` + desvío 0.61, 93 % y 85 % (v57, v58).

Pendiente: `suave_bajada` + `--log_std_init -0.5` (`cola_pendiente.txt`). Si confirma, cambiar el default de
`log_std_init` en `train.py`.

## 2026-10-15 · lucio · Las políticas bajan siempre a máxima velocidad; nueva recompensa por defecto `suave_bajada`

Medido con `tools/action_saturation.py`: en todas las políticas, `dz` está saturado en ~97 % de los pasos y `s = 1`
casi siempre; la media de la gaussiana de `dz` está entre 2 y 4. La política es casi bang-bang: se tira en picada
y corrige en horizontal, y por eso, si llega bajo y afuera, choca el borde (el modo de fallo de v17 y v21).

Castigar **estar** bajo y afuera (`borde_k1`, v28) hace que no baje nunca. Castigar **bajar** estando afuera y a
menos de 30 cm del tope (`reward_descent_coef`) funciona, pero solo junto con el castigo a la acción:

- `bajada_k03` sola: 26 % y 81 % (una seed flota).
- **`suave_bajada`** (`base` + `0.02·Σ(Δa)²` + `0.3·(d_xy − 0.25)₊·(bajada)₊/0.1`): **92 / 88 / 93 / 95 % con
  4 seeds** a 1.5M (v54, v56, v63, v64), contra 54 % de `base`. Choca el borde 5–13 veces de cada 100 (base:
  20–31) y es más suave.

**Decisión:** `suave_bajada` pasa a ser `DEFAULT_REWARD` (`utils.py`). Las corridas con `--load` siguen usando su
propia recompensa (`utils.run_reward`; `base` si son viejas).

Idea no probada: que la acción sea la velocidad directa (`v = 0.6·a`) o pasarla por `tanh`, para que los valores
intermedios sean naturales.

## 2026-10-24 · lucio (sesión de Claude) · Métricas de centrado, toque y suavidad del vuelo

`tools/evaluate.py` guarda ahora, en cada `eval_*.json`:
- **`landing`**: distancia horizontal al centro de la plataforma en los aterrizajes (`d_xy_mean`, `d_xy_median`,
  `d_xy_p90`) y fracción a menos de 5 y 10 cm (`within_5cm`, `within_10cm`).
- **`touchdown`**: en el último paso antes del primer contacto con el tope, velocidad de bajada relativa (`vz_*`,
  m/s) e inclinación (`tilt_deg_*`) y rebotes por episodio (`bounces_mean`).
- **`smoothness`**, además de lo que ya tenía: `cmd_vel_change_p95` (los saltos grandes de la velocidad pedida),
  `drone_jerk` (m/s³), `tilt_rms_deg` (inclinación RMS en vuelo) y `ang_vel_rms` (velocidad angular de roll y pitch).

Se reevaluaron best y final de todas las corridas con `eval_*.json` (v16–v64) y se evaluó el final de v16–v22, que no
lo tenía. Antes de pisar cada archivo se comprobó que el éxito, los `outcomes` y la suavidad vieja dieran igual.
`compare_runs` y `EXPERIMENTS.md` muestran las columnas nuevas.

Ejemplo, v54 (`suave_bajada`, final): aterriza a 8.1 cm del centro (mediana), solo 24 % a menos de 5 cm; llega a tocar
bajando a 0.45 m/s (mediana) y vuela con 8° de inclinación RMS.

## 2026-10-24 · lucio (sesión de Claude) · A 24 Hz, el PID del dron oscila solo (limitación del modelo, no error de código)

`BaseAviary.step` calcula las RPM una vez por paso de control (`_preprocessAction`) y las deja fijas los 10 pasos de
física. Con `ctrl_freq = 24`, el PID completo de `DSLPIDControl` (también el lazo de actitud) corre a 24 Hz. Medido con
una velocidad pedida **constante** de 0.3 o 0.6 m/s en +x, entre los segundos 2 y 4:

| Frecuencia del PID | Velocidad angular roll/pitch (RMS) | Inclinación máxima | vx |
|---|---|---|---|
| 24 Hz (la de hoy) | 1.50 rad/s | 8° | 0.61 ± 0.05 m/s |
| 48 Hz | 0.60 rad/s | 1.5° | 0.60 ± 0.01 |
| 120 y 240 Hz | 0.00 rad/s | 0.1° | 0.595 ± 0.000 |

Quieto en el lugar (hover) no oscila: aparece cuando se mueve en horizontal. Una política bang-bang (+x/−x cada 0.5 s)
llega a 4.5 rad/s RMS, y v54 vuela con ~2.2.

**No es un error del código**: la librería permite `ctrl_freq` < `pyb_freq` y hace exactamente eso. Pero no representa
al Crazyflie real, que corre el lazo de actitud a bordo a ~500 Hz, llegue el comando cada cuanto llegue. Consecuencias:
- Parte del bamboleo y de la inclinación que se mide en simulación (`tilt_rms_deg`, `ang_vel_rms`, `drone_jerk`) es
  un artefacto del modelo y **no se puede bajar con la recompensa**. Para comparar suavidad entre recompensas, la
  métrica que se transfiere al real es la de la **velocidad pedida** (`cmd_vel_change`, `cmd_vel_change_p95`).
- Probablemente vuelve más difícil la condición de aterrizaje (roll y pitch < 0.1 rad, 10 pasos seguidos).

**No se cambió nada** (Lucio prefiere medir primero las frecuencias reales en OptiTrack). Si se arregla, sería
correr `_preprocessAction` en cada paso de física con la última velocidad pedida, manteniendo la política a 24 Hz.
Cambia la dinámica: corrida aparte con su `base` de referencia. Anotado en `TODO_SIM2REAL.md`, punto 4 (desde el 2026-10-25, `SIM2REAL.md` en `~/Documents/Tesis/Laboratorio`).

## 2026-10-25 · lucio (sesión de Claude) · Castigar el salto de la velocidad pedida deja al dron flotando (v82)

`suave_bajada_v01` (`suave_bajada` + `0.1·|Δv_pedida/0.6|²`, seed 42): 0 %, flota los 100 episodios. La política pide
`s = 0` siempre: con velocidad pedida nula el castigo desaparece aunque la dirección sea ruido puro, así que es la
forma más barata de explorar. El castigo a la acción (`reward_action_coef`) no tiene esa salida porque también cobra
los cambios de `s`. Se descartan `_v01` y `_v03` (no se corren más seeds). En su lugar, para suavidad:
`suave_bajada_c005` (castigo a la acción 0.05) con `--log_std_init -0.5`, contra v65–v67.

## 2026-10-25 · lucio (sesión de Claude) · `suave_bajada` + desvío inicial 0.61: mismo éxito, más suave y más centrada

v65 / v66 / v67 (seeds 42 / 1 / 2, 1.5M, `--log_std_init -0.5`), modelo final en 100 episodios, contra `suave_bajada`
con el desvío por defecto (v54 / v56 / v63 / v64):

| | `suave_bajada` (4 seeds) | + desvío 0.61 (3 seeds) |
|---|---|---|
| Éxito final medio | 92 % (88–95) | 93 % (89 / 92 / 97) |
| Δv pedida por paso | 0.137 m/s | 0.083 m/s |
| Δacción por paso | 0.27 | 0.08 |
| Centro (mediana) / a menos de 5 cm | 8.2 cm / 21 % | 6.3 cm / 36 % |
| Velocidad al llegar a tocar (mediana) | 0.43 m/s | 0.48 m/s |
| Cruza 50 % en el entrenamiento | ~0.7M | ~1.0M |

- En éxito no hay diferencia. En suavidad y centrado sí, aunque no en todas las seeds: comparando seed por seed, la
  velocidad pedida es más suave en 2 de 3 (seed 1: 0.100 contra 0.091).
- Aprende más tarde (~0.3M pasos después) y sigue subiendo a 1.5M.
- No se cambió el default de `log_std_init` (queda anotado para que Lucio decida). Las variantes nuevas de suavidad
  se prueban con este desvío (`suave_bajada_c005`, v91–v93).

~~Otra cosa que mostraron las métricas nuevas: el castigo a la acción hace que toque más rápido.~~ **Falso, error
de la métrica:** `touchdown.vz` se medía al final del paso con contacto, cuando el choque ya había frenado al dron
(v67 marcaba 0.03 m/s y en realidad llega a 0.51). Arreglado en `tools/evaluate.py` (se mide en el último paso antes
del contacto) y reevaluadas todas las corridas: **todas llegan a tocar bajando a 0.41–0.48 m/s** (mediana), casi a la
velocidad máxima de bajada, sin diferencia entre recompensas. El centrado sí cambia (no dependía de esa métrica):
`base` 6.8 cm, `suave_c002` 8.5, `suave_bajada` 8.2, `suave_bajada` + desvío 0.61 6.3. `suave_bajada_flare` (v83, v86,
v89) ataca justamente la velocidad de llegada.

## 2026-10-25 · lucio (sesión de Claude) · Castigar la llegada rápida también deja al dron flotando (v83, v86)

`suave_bajada_flare` (castigo por bajar a más de 0.15 m/s alineado y a menos de 15 cm del tope): 0 % con las seeds 42 y
1; flota a 5–19 cm del tope, cerca del borde. Junto con el castigo por bajar afuera, bajar cerca del tope cuesta en
todas partes. Se descarta. Con esta ya son seis variantes que caen en la trampa de flotar (A1, B, XY, `borde_k1`,
`suave_bajada_v01` y `_flare`): **cualquier término que encarezca acercarse o bajar cerca de la plataforma desde el
principio del entrenamiento la provoca.** Lo que sí funcionó fue tocar solo el premio terminal (`suave_bajada_centro`,
v84: 96 %) y la exploración (`--log_std_init -0.5`). Idea para cuando se quiera atacar la velocidad de llegada: un
curriculum (entrenar con `suave_bajada` y seguir con `--load` agregando el término una vez que ya aterriza).

## 2026-10-25 · lucio (sesión de Claude) · Premio al centro (v84, v87) y castigo a la acción 0.05 con desvío 0.61 (v91)

- **`suave_bajada_centro`** (premio al aterrizar `25 − 100·d_xy` en vez de `25 − 50·d_xy`), desvío 1: 96 % (s42, v84)
  y 83 % (s1, v87), contra 92 % y 88 % de `suave_bajada` con las mismas seeds. **No centra mejor** (8.6 y 8.0 cm de
  mediana, contra 8.1 y 9.6). Hipótesis: el premio llega 10 pasos después de tocar y apoyado ya casi no se desplaza;
  el centrado se decide antes de tocar. Sin mejora clara con dos seeds; falta la seed 2 (v90) y la versión con
  desvío 0.61 (v94, v95).
- **`suave_bajada_c005`** (castigo a la acción 0.05 en vez de 0.02) + desvío 0.61, seed 42 (v91): **100 % en el modelo
  final, y 200/200 en 200 episodios extra con seeds distintas (1000–1199)**; v65 (misma seed, castigo 0.02): 92 % y
  189/200. Es la más suave (Δv pedida 0.051 m/s) y la más centrada (5.1 cm, 49 % a menos de 5 cm) del proyecto, y
  aprende antes. **Una sola seed**: faltan v92 y v93. Para ver hasta dónde se puede subir el castigo: `suave_bajada_c01`
  (0.1) con desvío 0.61 (v96, v97).

## 2026-10-25 · lucio (sesión de Claude) · Resultados con 2–3 seeds: `c005` es la más suave pero no siempre aprende a tiempo; `centro` y `c01` se descartan

Modelo final en 100 episodios, 1.5M pasos:

| Variante | Seeds 42 / 1 / 2 | Media | Δv pedida (las que aprenden) | Centro (mediana) |
|---|---|---|---|---|
| `suave_bajada` (control, desvío 1) | 92 / 88 / 93 % | 91 % | 0.114 m/s | 8.2 cm |
| `suave_bajada` + desvío 0.61 | 92 / 97 / 89 % | 93 % | 0.083 m/s | 6.3 cm |
| `suave_bajada_c005` + desvío 0.61 | **100 / 61 / 97 %** (s3: 72 %) | 82.5 % (4 seeds) | **0.049 m/s** | 5.1 / 12.3 / 6.3 cm |
| `suave_bajada_c01` + desvío 0.61 | 0 / 42 % | 21 % | | |
| `suave_bajada_centro` (desvío 1) | 96 / 83 / 87 % | 89 % | 0.087 m/s | 8.6 / 8.0 / 10.8 cm |
| `suave_bajada_centro` + desvío 0.61 | 92 / 94 % | 93 % | 0.084 m/s | 7.4 / 7.5 cm |

- **`c005` (castigo a la acción 0.05):** las seeds que aprenden son las más suaves y centradas del proyecto (v91: 100 %
  y 200/200 en seeds nuevas; v93: 97 %), pero con la seed 1 (v92) aprende recién a 1.3M y a 1.5M da 61 %. **El castigo
  más fuerte retrasa el aprendizaje según la seed.** La seed 3 (v98) también aprende tarde (72 %): 2 de 4 seeds.
- **`c01` (0.1):** frena el aprendizaje (0 % flotando quieta, y 42 %). Descartada. El límite está entre 0.05 y 0.1.
- **`centro` (premio terminal 25 − 100·d_xy):** no centra mejor ni con desvío 1 ni con 0.61, y el éxito queda igual.
  Descartada. El centrado se decide antes de tocar y el premio llega tarde.
- Recomendación (no se cambió ningún default): para un vuelo suave sin perder robustez, `suave_bajada` + desvío 0.61.
  Si se acepta entrenar más pasos, `suave_bajada_c005` + desvío 0.61 promete más suavidad: probarla a 3M o con 0.03.

## 2026-10-25 · lucio (sesión de Claude) · Entrenar más centra más: `suave_bajada` a 3M (v69)

`suave_bajada`, seed 42, 3M pasos (v69) contra 1.5M (v54): **99 % contra 92 %** (199/200 en seeds nuevas), y aterriza
a **3.7 cm del centro contra 8.1** (60 % contra 24 % a menos de 5 cm). La suavidad no cambia (Δv pedida 0.119 contra
0.100 m/s). Lo mismo se veía en v17 (`base`, 5M): 99 % y 6.5 cm. **El centrado y el último tramo de éxito vienen de
entrenar más, no de la recompensa** (el premio terminal al centro no centró). Una sola seed. Para la combinación
suave + exitosa + centrada, lo siguiente sería entrenar a 3M `suave_bajada` + desvío 0.61 y `c005` + desvío 0.61
(sus seeds lentas no terminan de aprender a 1.5M).

## 2026-10-25 · lucio (sesión de Claude) · Castigo a la acción 0.03 con desvío 0.61: la más robusta (v99, v101, v102)

`suave_bajada_c003` (castigo a la acción 0.03 en vez de 0.02) + `--log_std_init -0.5`, modelo final en 100 episodios:

| Castigo a la acción (+ desvío 0.61) | Seeds 42 / 1 / 2 | Media | Choques contra el borde (300 ep.) | Δv pedida | Centro |
|---|---|---|---|---|---|
| 0.02 (`suave_bajada`, v65–v67) | 92 / 97 / 89 % | 92.7 % | 18 | 0.083 m/s | 6.3 cm |
| **0.03 (`c003`, v101, v99, v102)** | **95 / 99 / 99 %** | **97.7 %** | **4** | 0.081 m/s | 6.2 cm |
| 0.05 (`c005`, v91–v93; s3 v98: 72 %) | 100 / 61 / 97 % | 86 % | 31 | 0.051 m/s | |
| 0.1 (`c01`, v96, v97) | 0 / 42 % | | | | |

- Con 0.03 aprenden las 3 seeds a tiempo (100 % en los evals de 8 episodios desde ~1.0M) y fallan menos que con 0.02.
  La suavidad es la misma que con 0.02; la diferencia está en el éxito. Los intervalos de cada seed se pisan, pero la
  mejora va en el mismo sentido en las 3.
- 0.05 es más suave (Δv pedida ~0.05) pero con la mitad de las seeds aprende tarde; 0.1 no aprende.
- **Recomendación (no se cambió ningún default):** `suave_bajada_c003` + `--log_std_init -0.5`. Y entrenar más (3M):
  con `suave_bajada`, pasar de 1.5M a 3M subió el éxito de 92 a 99 % y centró de 8.1 a 3.7 cm (v69).

## 2026-10-25 · lucio (sesión de Claude) · A las seeds lentas de `c005` les faltaban pasos (v100)

`suave_bajada_c005` + desvío 0.61 con la seed 1 a 3M (v100): **100 %** (200/200 en seeds nuevas), contra 61 % de la
misma corrida a 1.5M (v92). Termina de aprender entre 1.5M y 1.8M. Es la más centrada del proyecto (3.3 cm de mediana,
71 % a menos de 5 cm) y, ya aprendida, la suavidad queda en Δv pedida 0.072 m/s (`suave_bajada` a 3M, v69: 0.119).

Con v69 (`suave_bajada` a 3M: 99 %, 3.7 cm), el patrón de la noche es: **a 1.5M pasos las comparaciones de recompensa
están contaminadas por la velocidad de aprendizaje.** Un castigo a la acción más fuerte da un vuelo más suave pero
aprende más lento; a 3M las dos dan ~100 % y centran mucho mejor. Para elegir la recompensa final conviene comparar a
3M (corre `c003` + desvío 0.61 a 3M, v103).

## 2026-10-25 · lucio (sesión de Claude) · A 3M pasos, `c003` y `c005` (con desvío 0.61) aterrizan siempre; cierre de la noche

v103 (`c003`, seed 42) y v104 (`c005`, seed 3) a 3M se cortaron por un apagado de la notebook (~11:00), en 2.81M y
2.95M: no hay modelo final. Se evaluó el best (`eval_best.json`; estado en `run.json` cambiado a mano a `interrupted`).

| Corrida (desvío 0.61, salvo v69) | Pasos | Éxito (100 ep.) | Centro / < 5 cm | Δv pedida |
|---|---|---|---|---|
| v69 `suave_bajada` (desvío 1), s42 | 3M, final | 99 % (199/200 extra) | 3.7 cm / 60 % | 0.119 m/s |
| v100 `c005`, s1 | 3M, final | 100 % (200/200 extra) | 3.3 cm / 71 % | 0.072 m/s |
| v103 `c003`, s42 | best de 2.4M | 100 % | 4.0 cm / 61 % | 0.064 m/s |
| v104 `c005`, s3 | best de 2.9M | 100 % | 4.5 cm / 54 % | 0.049 m/s |

**Conclusión de la noche:** a 1.5M pasos, las diferencias entre recompensas son sobre todo de velocidad de
aprendizaje. A 3M, todas las variantes con castigo a la acción y desvío 0.61 aterrizan en ~100 % y centran a ~4 cm.
Para un vuelo suave, el castigo a la acción 0.05 (`c005`) es el más suave (Δv pedida ~0.05–0.07 contra ~0.12 de
`suave_bajada` sola a 3M), pero necesita los 3M; `c003` es casi igual de suave y aprende a tiempo con todas las seeds.
Una sola seed por variante a 3M. Nada de esto cambió los defaults (`DEFAULT_REWARD`, `log_std_init`): lo decide Lucio.

## 2026-10-25 · lucio · Las colas ya no reservan números de corrida

Reservar números en `cola_pendiente.txt` dejaba huecos (v31, v32, v37–v39, v43–v49, v59–v62, v68, v70–v81, v85, v88,
v89 no existen) y obligaba a saltearlos. Ahora `tools/run_queue.py` asigna el siguiente número libre al lanzar cada
corrida y marca la línea como `# lanzada como v<N>-<autor>`. `cola_pendiente.txt` se reescribió sin números, con lo que
sigue teniendo sentido.

## 2026-10-25 · lucio (sesión de Claude) · Huecos de numeración: qué eran y cuáles se corren

Del registro de la sesión del 2026-10-15 se recuperó para qué se habían reservado los números que nunca se usaron:
v31 `suave_c005` s42, v32 `PBRS_k3` s42, v37 `combo_k3_c002` s42, v38 `suave_c01` s42, v39 `borde_k02` s42,
v43/v48 `PBRS_k10` s1/s2, v44/v49 `A2_k1` s1/s2, v45/v46/v47 seed 4 de `base`/`A2_k3`/`suave_c002`, v59 `suave_c002`
+ desvío 0.61 s2, v60–v62 `base` + desvío 0.37 (s42, 1, 2). Muchas se volvieron a reservar después con otro número
(v68, v70–v81), y por eso había tantos huecos.

Se corren con su número original las que siguen teniendo sentido (`cola_huecos.txt`, borrada al terminar): v59, v60–v62, v43, v48, v44 y v49.
Las demás no (`suave_c005` y `suave_c01` ya se probaron sobre `suave_bajada`; `PBRS_k3`, `combo_k3_c002` y `borde_k02`
son familias descartadas; una quinta seed de `base`, `A2_k3` o `suave_c002` no cambia nada), ni las descartadas de
esta noche (v85, v88: `suave_bajada_v01`; v89: `suave_bajada_flare`). Los números duplicados (v68, v70–v74) y los de
pruebas descartadas quedan como huecos para siempre.

## 2026-10-25 · lucio (sesión de Claude) · Menos ruido de exploración: 0.37 ayuda un poco más; y con 0.61 el término de bajada no suma

Corridas con número reservado del 2026-10-15 (modelo final, 100 episodios):

- **`base` con desvío inicial 0.37** (`--log_std_init -1.0`, v60/v61/v62, seeds 42/1/2): 78 / 91 / 87 % → **85 %**, contra
  79 % con desvío 0.61 (v50–v52) y 49 % con desvío 1. Sigue mejorando con menos ruido, pero de 0.61 a 0.37 la mejora es
  chica (mejor en 2 de 3 seeds, intervalos que se pisan) y aprende más tarde y de forma más irregular. Idea en `TODO.md`:
  probar 0.37 con `suave_bajada_c003`.
- **`suave_c002` + desvío 0.61, tercera seed** (v59, seed 2): 100 %. Con las 3 seeds (v57, v58, v59): 93 / 85 / 100 % →
  **92.7 %, lo mismo que `suave_bajada` + desvío 0.61** con las mismas seeds (v65–v67: 92 / 97 / 89 → 92.7 %), con los
  mismos choques contra el borde (16 contra 18 en 300 episodios), la misma suavidad y el mismo centrado. **Con desvío
  0.61, el castigo por bajar estando afuera (`reward_descent_coef`) no suma**: hacía falta con desvío 1, porque sin él
  `suave_c002` chocaba el borde (20–26 de 100). Tenerlo en cuenta al elegir la recompensa final.

## 2026-10-25 · lucio (sesión de Claude) · `PBRS_k10` y `A2_k1` con 3 seeds: no sirven

Las otras dos seeds (números reservados del 2026-10-15), modelo final en 100 episodios:

- **`PBRS_k10`** (v25, v43, v48; seeds 42 / 1 / 2): **72 / 1 / 3 % → 25 %**. Con las seeds 1 y 2 queda flotando. Solo la 42
  salió de la trampa (a 1.2M). La conclusión del 2026-10-15 ("aprende tarde, pero llega a lo mismo que `base`") era
  optimista por usar una sola seed.
- **`A2_k1`** (v26, v44, v49): **74 / 0 / 72 % → 49 %**, el mismo patrón que `base` con desvío 1 (72 / 0 / 76 %): con la seed 1
  flota. El progreso con k = 1 no cambia nada.

Con desvío 1, la seed 1 es la que separa las recompensas robustas de las que no: flotan `base`, `PBRS_k10` y `A2_k1`;
aprenden `A2_k3` (tarde), `suave_c002`, `suave_bajada` y todas las de desvío 0.61. Con esto se terminaron las corridas
que tenían número reservado y seguían teniendo sentido (`cola_huecos.txt`, ya borrada).

## 2026-10-30 · teo (sesión de Claude) · Primera noche en el laboratorio S004: 31 corridas de 3M (v105–v135)

Primera vez que se entrena en las máquinas de la universidad (`docs/laboratorio-s004-ssh.md`): 3 corridas de 3M en
paralelo, de 00:29 a 06:41, ~31–41 min por corrida. Todas terminaron bien. Modelo final en 100 episodios, seeds 42 / 1
/ 2 salvo que se diga otra cosa; todas con desvío inicial 0.61 (`--log_std_init -0.5`) salvo gSDE y la de 0.37:

| Variante | Corridas | Éxito | Δv pedida (media) | Centro | Toca a |
|---|---|---|---|---|---|
| `c003` | v105–v107 | 100 / 100 / 100 % | 0.066 m/s | 4.1 / 4.5 / 3.7 cm | 0.50 m/s |
| `c005` (5 seeds, con v100-lucio) | v108, v109, v110, v114, v100 | 100 / **0** / 97 / 100 / 100 % | 0.060 (sin v109) | 3.3–4.7 cm | 0.50 |
| `suave_bajada` (control) | v130–v132 | 100 / 100 / 100 % | 0.079 | 4.6 / 3.3 / 4.7 | 0.50 |
| `c003` + desvío 0.37 | v133–v135 | 100 / 100 / 100 % | 0.064 | 3.5 / 3.2 / 3.2 | 0.51 |
| `c003` + gSDE | v118–v120 | 100 / 100 / 100 % | 0.056 | 4.2 / 3.3 / 3.2 | 0.50 |
| `c003` + CAPS | v121–v123 | 100 / 100 / 100 % | 0.058 | **2.7** / 3.2 / 3.8 | 0.50 |
| `c003` + premio por tocar despacio | v111–v113 | 100 / 100 / 100 % | 0.084 | 5.3 / 4.3 / 3.8 | 0.45 |
| `c003` + efecto suelo | v115–v117 | 100 / 99 / 98 % | 0.081 | 3.6 / 4.3 / 4.2 | 0.40 |
| `c003` + acción como velocidad | v124–v126 | 100 / 91 / 100 % | 0.087 | 3.7 / 4.8 / 5.1 | 0.50 |
| `c003` + velocidad + premio por tocar | v127–v129 | 100 / 100 / 99 % | 0.082 | 3.7 / 5.2 / 4.7 | **0.33** / 0.45 / 0.46 |

Las conclusiones van en las entradas siguientes. Las opciones nuevas del entorno y de `train.py` (efecto suelo, acción
como velocidad, premio por tocar despacio, gSDE, CAPS, `--init_from`) están apagadas por defecto; ninguna cambió un
default. Las ideas de la literatura que llevaron a estas pruebas, y las que faltan, están en
`docs/estado-del-arte-2026-10-30.md`.

## 2026-10-30 · teo (sesión de Claude) · Candidatas a 3M: `c003` aterriza siempre, `c005` a veces flota, y `suave_bajada` también llega a 100 %

- **`c003` a 3M** (v105–v107): 100 % con las 3 seeds, Δv pedida 0.063–0.072 m/s, 4 cm del centro. Repite completa v103,
  que se había cortado.
- **`c005` a 3M**, con 5 seeds (v108, v109, v110, v114 y v100-lucio): 100 / **0** / 97 / 100 / 100 %. Es la más suave
  cuando aprende (v108: 0.043 m/s), pero **v109 (seed 2) se quedó flotando los 480 pasos con `s = 0`**: con el castigo
  a la acción, no moverse no cuesta nada. **La misma seed aprendió en la máquina de Lucio** (v93, a 1.5M): con
  subprocesos y otro hardware el entrenamiento no es reproducible, así que caer en la trampa es cuestión de azar y no
  de la seed. Con 1 falla en 5, `c005` es frágil.
- **Control, `suave_bajada` a 3M con desvío 0.61** (v130–v132): también 100 % en las 3 seeds (a 1.5M, v65–v67: 92.7 %),
  con Δv pedida 0.069–0.098 m/s. **Lo que más mejoró de 1.5M a 3M fue entrenar más tiempo, no el castigo a la acción.**
  `c003` es algo más suave en promedio (0.066 contra 0.079), pero las seeds se superponen.
- **Recomendación (no se cambió ningún default):** `suave_bajada_c003` con desvío 0.61 y 3M pasos. Con desvío 0.37
  (v133–v135) centra mejor (3.2–3.5 cm), con la misma suavidad, pero aprende ~0.5M pasos más tarde. Lo decide Lucio.

## 2026-10-30 · teo (sesión de Claude) · La política nunca frena: `s` saturado en 1 el 100 % de los pasos

Todas las políticas tocan la plataforma bajando a ~0.5 m/s (la velocidad máxima es 0.6). `tools/action_saturation.py`
muestra por qué: **la salida `s` (fracción de la velocidad máxima) está en 1 en el 100 % de los pasos**, con la media
de la gaussiana en ~3. Con la acción de gym-pybullet-drones (`v = 0.6·s·dir/|dir|`), **el dron vuela siempre a 0.6 m/s**,
y para bajar más lento tiene que inclinar la dirección hacia los costados. Con media 3 y desvío ~0.6, la exploración
casi nunca prueba `s < 1`. Esto explica tres cosas:
- por qué castigar (`_flare`, v83, v86) o premiar la velocidad de toque no le enseña a frenar;
- por qué la salida de la trampa de `c005` y `suave_bajada_v01` es pedir `s = 0`;
- por qué `dz` sale saturado (60–85 % de los pasos a 3M).

Lo que se probó:
- **Premio por tocar despacio** (`landing_vz_coef: 10`: al aterrizar, `+10·(1 − v_toque/0.6)`; se paga una vez y solo
  si aterriza, así que no causa la trampa de flotar). Con la acción de siempre (`c003_tocar`, v111–v113): 100 %, pero
  toca a 0.43–0.47 m/s. **Casi no frena.**
- **Acción como velocidad** (`action_mode: velocity`: `v = 0.6·(dx, dy, dz)`, recortada a norma 1, sin usar `s`). Sola
  (`c003_vel`, v124–v126): aprende antes (50 % a ~0.5M contra ~0.7M), pero es menos suave (0.087 m/s) y toca igual a
  0.5 m/s. Poder frenar no alcanza si nada lo pide.
- **Velocidad + premio por tocar** (`c003_vel_tocar`, v127–v129): **v127 toca a 0.33 m/s de mediana (p90 0.43)**, la más
  lenta del proyecto (la siguiente es v17-lucio, con 0.38). Las otras dos seeds tocan a 0.45–0.46. **Frenar se puede
  aprender, pero lo descubre 1 seed de 3.**

Hipótesis: la exploración casi no prueba valores intermedios de `dz`, porque su media está en ~1.6–1.9, muy afuera de
[−1, 1]. Además, el premio por frenar es chico (pasar de 0.5 a 0.33 m/s suma ~2.8, contra ~23 por aterrizar).
Próximas pruebas (`TODO.md`): curriculum desde v127 con más premio, el premio a 25 desde cero, y castigar que la media
de la gaussiana se salga de [−1, 1].

## 2026-10-30 · teo (sesión de Claude) · Suavidad sin tocar la recompensa: gSDE y CAPS suavizan poco, pero centran mejor

Dos ideas de la literatura que suavizan sin cambiar la recompensa (no pueden causar la trampa de flotar), con
`suave_bajada_c003` a 3M, contra v105–v107:
- **gSDE** (`--use_sde --sde_sample_freq 4 --log_std_init -2`, v118–v120): ruido de exploración que depende del estado
  y se sortea cada 4 pasos. Δv pedida 0.056 contra 0.066 m/s (~15 % menos) y centro 3.2–4.2 cm. v119 parecía mucho
  mejor (0.046 m/s, 81 % a menos de 5 cm); con 3 seeds, la mejora es modesta.
- **CAPS** (`caps.py`, `--caps_temporal 0.01 --caps_spatial 0.01`, v121–v123): dos términos en la pérdida de PPO que
  castigan que la media de la acción cambie entre pasos seguidos y ante ruido en la observación. Δv pedida 0.058 m/s
  (~12 % menos), pero **el mejor centrado del proyecto**: 2.7 / 3.2 / 3.8 cm, 68–84 % a menos de 5 cm.
  Hipótesis de por qué suaviza poco: CAPS actúa sobre la media de la gaussiana sin recortar, que está muy afuera de
  [−1, 1], así que gran parte del término castiga cambios que no cambian la acción ejecutada. El término espacial
  crece durante el entrenamiento (0.08 → 0.2).
- **Desvío inicial 0.37** (v133–v135), para comparar: también centra mejor (3.2–3.5 cm) y no suaviza.

Las tres centran mejor que `c003` con desvío 0.61, y ninguna resuelve la suavidad: el castigo a la acción en la recompensa (`c003`, `c005`) sigue siendo lo que más
suaviza. gSDE y CAPS no cuestan éxito y se pueden combinar con lo que se elija.

## 2026-10-30 · teo (sesión de Claude) · Efecto suelo contra el tope de la plataforma

La simulación usaba `Physics.PYB`, sin efecto suelo. El de gym-pybullet-drones (`PYB_GND`) mide la altura contra el
piso, y el tope está a 0.35 m. Se agregó `ground_effect: true` (`env.py`, `_groundEffect`, apagado por defecto): el
mismo modelo de la librería, pero cada hélice mide su altura contra el tope si está encima de la plataforma. En hover
da +4 % de empuje a 10 cm, +15 % a 5 cm y +27 % por debajo de 3.8 cm; en el borde, con 2 hélices adentro, +13.5 % y
además inclina. `ground_effect_scale` lo escala.

- **Entrenar con efecto suelo** (`c003_gnd`, v115–v117): 100 / 99 / 98 %, tocando a 0.38–0.41 m/s (el colchón de aire
  frena). 2 de 3 seeds aprenden más tarde (50 % a 1.0–1.3M).
- **Prueba cruzada** (50 episodios): las políticas entrenadas con efecto suelo y sin él aterrizan 50 de 50 con el
  efecto ×0, ×0.3, ×1 y ×1.5. Con este modelo, el efecto suelo amortigua y no compromete el aterrizaje.
- **La magnitud es dudosa:** el modelo da ~18 % a 4.6 cm, y mediciones publicadas en un Crazyflie 2.0 dan ~5 %. Hay que
  medirlo en el laboratorio y, mientras tanto, aleatorizar la escala (`TODO.md`, punto 7).

## 2026-10-31 · teo (sesión de Claude) · Dejar a Claude entrenando por SSH: qué falló y cómo se evita

La noche del 2026-10-29, las 31 corridas terminaron bien, pero Claude solo trajo y registró hasta v119. Las otras 16
(v120–v135) se trajeron recién la noche del 31. Pasaron tres cosas:
- la espera en segundo plano (`until ssh ...; do sleep 60; done`) se trabó sin dejar errores, probablemente por la
  conexión SSH compartida (`ControlMaster`);
- Claude solo se despertaba si se cumplía la condición, y como nunca se cumplió, no volvió a mirar;
- a las 07:00 se cortaron el SSH (como todos los días hábiles) y la VPN, ~8 h después de levantarla.

No se perdió nada, porque `runs/` está en el home del laboratorio. Las reglas nuevas, y los comandos probados, están en
`docs/laboratorio-s004-ssh.md`, "Dejar a Claude entrenando solo": tope de tiempo en cada `ssh`, espera que sale a los
30 min aunque no pase nada, traer cada corrida apenas termina y contar con que la VPN dura ~8 h.
