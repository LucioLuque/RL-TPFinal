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
Cambia la dinámica: corrida aparte con su `base` de referencia. Anotado en `TODO_SIM2REAL.md`, punto 4.

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
| `suave_bajada_c005` + desvío 0.61 | **100 / 61 / 97 %** | 86 % | **0.051 m/s** | 5.1 / 12.3 / 6.3 cm |
| `suave_bajada_c01` + desvío 0.61 | 0 / 42 % | 21 % | | |
| `suave_bajada_centro` (desvío 1) | 96 / 83 / 87 % | 89 % | 0.087 m/s | 8.6 / 8.0 / 10.8 cm |
| `suave_bajada_centro` + desvío 0.61 | 92 / 94 % | 93 % | 0.084 m/s | 7.4 / 7.5 cm |

- **`c005` (castigo a la acción 0.05):** las seeds que aprenden son las más suaves y centradas del proyecto (v91: 100 %
  y 200/200 en seeds nuevas; v93: 97 %), pero con la seed 1 (v92) aprende recién a 1.3M y a 1.5M da 61 %. **El castigo
  más fuerte retrasa el aprendizaje según la seed.** Corre la seed 3 (v98) para ver qué tan seguido pasa.
- **`c01` (0.1):** frena el aprendizaje (0 % flotando quieta, y 42 %). Descartada. El límite está entre 0.05 y 0.1.
- **`centro` (premio terminal 25 − 100·d_xy):** no centra mejor ni con desvío 1 ni con 0.61, y el éxito queda igual.
  Descartada. El centrado se decide antes de tocar y el premio llega tarde.
- Recomendación (no se cambió ningún default): para un vuelo suave sin perder robustez, `suave_bajada` + desvío 0.61.
  Si se acepta entrenar más pasos, `suave_bajada_c005` + desvío 0.61 promete más suavidad: probarla a 3M o con 0.03.
