# Pruebas de suavidad, centrado y exploración (2026-10-24/25)

Lucio (sesiones con Claude). Rama `suavidad-y-centro`. 34 corridas nuevas: v43, v44, v48, v49, v59–v62, v65–v67, v69,
v82–v84, v86, v87 y v90–v104. Todas en `runs/`, con su `NOTES.md`. La bitácora tiene una entrada por prueba (2026-10-24
y 2026-10-25); este documento las junta.

**Para leer rápido:** el [Resumen](#resumen), las [Tres políticas candidatas](#tres-políticas-candidatas) y
[Cómo seguir](#cómo-seguir).

## Resumen

- **Métricas nuevas** en la evaluación de 100 episodios: qué tan centrado aterriza, cómo llega a la plataforma y qué
  tan suave vuela. Se reevaluaron todas las corridas viejas (mismo éxito que antes).
- **Menos ruido de exploración** (`--log_std_init -0.5`, desvío inicial 0.61) con `suave_bajada`: mismo éxito (93 %
  contra 92 %), vuelo más suave (la velocidad pedida salta 0.083 contra 0.137 m/s por paso) y más centrado (6.3 contra
  8.2 cm).
- **Castigo a la acción 0.03** (`suave_bajada_c003`) con desvío 0.61: **97.7 % con 3 seeds**, la recompensa más robusta
  a 1.5M pasos. Con 0.05 (`c005`) es más suave, pero la mitad de las seeds aprende tarde; con 0.1 no aprende.
- **Entrenar 3M pasos** en vez de 1.5M lleva a ~100 % y **centra mucho más** (3–4 cm contra 6–8 cm). A las seeds lentas
  de `c005` les faltaban pasos: a 3M llegan a 100 %.
- **No sirvieron:** castigar el salto de la velocidad pedida o la llegada rápida (el dron queda flotando), el premio
  terminal al centro (no centra) y el castigo a la acción 0.1.
- **Con desvío 0.61, el término de bajada de `suave_bajada` no suma:** `suave_c002` da lo mismo (92.7 % las dos).
- **Hallazgo del simulador:** con el PID del dron a 24 Hz (la frecuencia de la política), el dron simulado oscila solo,
  aun con una velocidad pedida constante. No es un error del código; está anotado para medirlo en el laboratorio.
- **No se cambió ningún default** (`DEFAULT_REWARD`, `log_std_init`): se espera a las corridas a 3M con 3 seeds.

## Métricas nuevas

`tools/evaluate.py` guarda en cada `eval_*.json`, además de lo que ya tenía:

| Bloque | Qué mide |
|---|---|
| `landing` | Distancia horizontal al centro de la plataforma en los aterrizajes: media, mediana, p90 y fracción a menos de 5 y 10 cm |
| `touchdown` | En el último paso antes de tocar el tope: velocidad de bajada y inclinación. Y rebotes por episodio |
| `smoothness` | Además de `action_change`, `cmd_vel_change` y `drone_accel`: `cmd_vel_change_p95` (los saltos grandes de la velocidad pedida), `drone_jerk`, `tilt_rms_deg` y `ang_vel_rms` |

Se reevaluaron best y final de todas las corridas con evaluación (v16–v64), y se evaluó el final de v16–v22, que no lo
tenían. Antes de pisar cada archivo se comprobó que el éxito, los `outcomes` y la suavidad vieja dieran igual.
`compare_runs` y `EXPERIMENTS.md` muestran las columnas nuevas, y `eval.py` imprime centro, tiempo y suavidad por episodio.

Dos cosas para leerlas:
- **La suavidad que importa es la de la velocidad pedida** (`cmd_vel_change`): es lo que se le manda al Crazyflie real.
  La inclinación, el jerk y la velocidad angular están contaminados por el bamboleo del PID a 24 Hz (abajo).
- **Una corrección:** la primera versión de `touchdown` medía la velocidad al final del paso en que hubo contacto, cuando
  el choque ya había frenado al dron (v67 daba 0.03 m/s y en realidad llega a 0.51). Se arregló y se reevaluó todo. Con
  la métrica correcta, **todas las políticas llegan a tocar bajando a 0.41–0.51 m/s**, sin diferencia entre recompensas.

## Lo que se probó

Modelo final en 100 episodios, 1.5M pasos salvo que se diga otra cosa. "Δv pedida" = cambio medio por paso de la
velocidad pedida (más chico = más suave). "Centro" = mediana de la distancia al centro en los aterrizajes.

### Por recompensa (todas las seeds)

| Recompensa | Seeds | Éxito final por seed | Medio | Δv pedida | Centro | < 5 cm |
|---|---|---|---|---|---|---|
| `base` | 4 | 0 / 76 / 70 / 72 % (s1 / s2 / s3 / s42) | 54 % | 0.227 | 6.9 cm | 29 % |
| `base` + desvío 0.61 | 3 | 79 / 76 / 81 % (s1 / s2 / s42) | 79 % | 0.194 | 6.9 cm | 34 % |
| `base` + desvío 0.37 | 3 | 91 / 87 / 78 % | 85 % | 0.163 | 7.5 cm | 24 % |
| `suave_c002` | 4 | 76 / 75 / 71 / 72 % | 74 % | 0.112 | 8.5 cm | 20 % |
| `suave_c002` + desvío 0.61 | 3 | 85 / 100 / 93 % | 93 % | 0.097 | 6.1 cm | 35 % |
| `suave_bajada` (default) | 4 | 88 / 93 / 95 / 92 % | 92 % | 0.137 | 8.2 cm | 21 % |
| `suave_bajada` + desvío 0.61 | 3 | 97 / 89 / 92 % | 93 % | 0.083 | 6.3 cm | 36 % |
| **`suave_bajada_c003` + desvío 0.61** | 3 | **99 / 99 / 95 %** | **98 %** | 0.081 | 6.2 cm | 38 % |
| `suave_bajada_c005` + desvío 0.61 | 4 | 61 / 97 / 72 / 100 % | 82 % | **0.049** | 9.3 cm | 26 % |
| `suave_bajada_c01` + desvío 0.61 | 2 | 42 / 0 % | 21 % | | | |
| `suave_bajada_centro` | 3 | 83 / 87 / 96 % | 89 % | 0.087 | 9.1 cm | 18 % |
| `suave_bajada_centro` + desvío 0.61 | 2 | 94 / 92 % | 93 % | 0.084 | 7.4 cm | 27 % |
| `PBRS_k10` | 3 | 1 / 3 / 72 % | 25 % | | | |
| `A2_k1` | 3 | 0 / 72 / 74 % | 49 % | | | |
| `suave_bajada_v01` | 1 | 0 % | 0 % | | | |
| `suave_bajada_flare` | 2 | 0 / 0 % | 0 % | | | |

(`python -m tools.compare_runs <corridas> --by-reward`; las columnas de suavidad y centro son de las seeds que aprendieron.)

### 1. Menos ruido de exploración (v65–v67, v60–v62, v59)

- `suave_bajada` + desvío 0.61: mismo éxito que con desvío 1, más suave y centrada. Aprende ~0.3M pasos más tarde.
- `base` + desvío 0.37: 85 % contra 79 % con 0.61 y 49 % con 1. Sigue ayudando, pero poco, y aprende más tarde.
- Tercera seed de `suave_c002` + desvío 0.61 (v59, 100 %): con 3 seeds da 92.7 %, **lo mismo que `suave_bajada` + desvío
  0.61**, con los mismos choques contra el borde (16 contra 18 en 300 episodios). El término de bajada
  (`reward_descent_coef`) hacía falta con desvío 1, porque sin él `suave_c002` chocaba el borde; con desvío 0.61 no suma.

### 2. Variantes para un vuelo más suave que cayeron en la trampa de flotar (v82, v83, v86)

- **Castigo al salto de la velocidad pedida** (`suave_bajada_v01`, `0.1·|Δv/0.6|²`): 0 %. La política pide `s = 0`
  (velocidad nula) siempre: así el castigo desaparece aunque la dirección sea ruido. El castigo a la acción no tiene esa
  salida porque también cobra los cambios de `s`.
- **Castigo por llegar rápido a la plataforma** (`suave_bajada_flare`): 0 % con 2 seeds. Junto con el castigo por bajar
  afuera, bajar cerca del tope cuesta en todos lados y el agente deja de intentarlo.
- Con estas, son seis las variantes del proyecto que flotan (A1, B, XY, `borde_k1`, `v01`, `flare`): **cualquier término
  que encarezca acercarse o bajar cerca de la plataforma desde el principio del entrenamiento lo provoca.**

### 3. Premio al centro (v84, v87, v90, v94, v95)

Premio al aterrizar `25 − 100·d_xy` en vez de `25 − 50·d_xy`. **No centra mejor** (9.1 cm contra 8.2 con desvío 1; 7.4
contra 6.3 con desvío 0.61) y el éxito queda igual. Hipótesis: el premio llega 10 pasos después de tocar, cuando apoyado
ya casi no se mueve; el centrado se decide antes.

### 4. Castigo a la acción más fuerte, con desvío 0.61 (v91–v93, v98, v96, v97, v99, v101, v102)

| Castigo | Éxito por seed | Medio | Δv pedida | Cuándo aprende |
|---|---|---|---|---|
| 0.02 (`suave_bajada`) | 92 / 97 / 89 % (s42 / s1 / s2) | 93 % | 0.083 | ~1.0M |
| **0.03** (`c003`) | **95 / 99 / 99 %** | **98 %** | 0.081 | ~1.0M en las 3 |
| 0.05 (`c005`) | 100 / 61 / 97 % (+ s3: 72 %) | 82 % | 0.049 | dos seeds recién a 1.1–1.3M |
| 0.1 (`c01`) | 0 / 42 % | | | no aprende o muy tarde |

Más castigo a la acción da un vuelo más suave, pero aprende más lento. Con 0.03 todas las seeds llegan a tiempo y chocan
menos el borde (4 contra 18 en 300 episodios); la suavidad es la misma que con 0.02.

### 5. Más pasos: 3M (v69, v100, v103, v104)

| Corrida | Recompensa | Éxito | Centro / < 5 cm | Δv pedida |
|---|---|---|---|---|
| v69 | `suave_bajada`, s42 (1.5M: v54, 92 %) | 99 % (199/200 en seeds nuevas) | 3.7 cm / 60 % | 0.119 |
| v100 | `c005` + desvío 0.61, s1 (1.5M: v92, 61 %) | 100 % (200/200) | 3.3 cm / 71 % | 0.072 |
| v103 | `c003` + desvío 0.61, s42 — **cortada en 2.8M**, best de 2.4M | 100 % | 4.0 cm / 61 % | 0.064 |
| v104 | `c005` + desvío 0.61, s3 — **cortada en 2.95M**, best de 2.9M | 100 % | 4.5 cm / 54 % | 0.049 |

**A 1.5M pasos, las diferencias entre recompensas son sobre todo de velocidad de aprendizaje.** A 3M todas llegan a
~100 % y centran a 3–4 cm. v103 y v104 se cortaron por un apagado de la notebook: no tienen modelo final y se evaluó su
best (`run.json` con estado `interrupted`).

## Hallazgo: el PID del dron simulado corre a 24 Hz y oscila

`BaseAviary.step` calcula las RPM una vez por paso de control y las deja fijas los 10 pasos de física, así que el PID del
dron corre a la frecuencia de la política (24 Hz). Con una velocidad pedida **constante** en horizontal:

| PID | Inclinación máxima | La velocidad varía |
|---|---|---|
| 24 Hz (hoy) | 8° | ±0.05–0.07 m/s |
| 48 Hz | 1.5° | ±0.01 m/s |
| 120–240 Hz | 0.1° | nada |

No es un error del código (la librería lo permite), pero el Crazyflie real controla a bordo a ~500 Hz. Consecuencias: la
inclinación y el jerk medidos en simulación tienen un piso que la recompensa no puede bajar, y a 0.6 m/s la simulación
inclina al dron hasta 20–28° (el real limita a 20°). **No se cambió:** primero hay que medir en el laboratorio cómo
responde el dron real (escalones de velocidad, `~/Documents/Tesis/Laboratorio`).

## Cambios en el código

Con los defaults, el entorno da exactamente lo mismo que antes (verificado: diferencia 0 en recompensa y observación).

- `env.py`: términos de recompensa nuevos, apagados por defecto: `reward_cmd_vel_coef` (salto de la velocidad pedida),
  `reward_ang_vel_coef` (bamboleo), `reward_flare_coef` (llegada rápida) y `landing_dxy_coef` (pendiente del premio al
  aterrizar; default 50, como antes).
- `rewards.yaml`: variantes `suave_bajada_v01`, `_v03`, `_centro`, `_flare`, `_w`, `_c003`, `_c005` y `_c01`, con su
  resultado en el comentario.
- `tools/evaluate.py`: las métricas nuevas. `eval.py`: centro, tiempo y suavidad por episodio y en resumen.
- `tools/compare_runs.py` y `tools/experiments_index.py`: columnas de centrado y suavidad.
- `tools/run_queue.py`: el número de corrida se asigna al lanzar (la cola ya no lleva números reservados, que dejaban
  huecos). Las colas viejas, con el número adelante, siguen funcionando.
- `TODO.md` y `cola_pendiente.txt` quedan solo con lo pendiente (lo hecho se borra). Lo del robot real
  (`TODO_SIM2REAL.md`) pasó a `~/Documents/Tesis/Laboratorio`.

## Tres políticas candidatas

No se elige una todavía (ni se cambia el default): hace falta correr las candidatas a 3M con 3 seeds. Las tres, con
desvío inicial 0.61 salvo la última:

| | Corrida para mirar | Ventajas | Desventajas |
|---|---|---|---|
| **`suave_bajada_c003` + desvío 0.61** | v99, v101, v102 (1.5M) | La más robusta: 97.7 % con 3 seeds, todas aprenden a tiempo; la que menos choca el borde; se entrena en 1.5M | Igual de suave que `suave_bajada` con desvío 0.61 (Δv pedida 0.081), centrado de 6 cm a 1.5M; a 3M solo hay un best de una corrida cortada (v103: 100 %, 4 cm) |
| **`suave_bajada_c005` + desvío 0.61, a 3M** | v100 (3M) | La más suave (Δv pedida 0.049–0.072) y la más centrada (3.3 cm, 71 % a menos de 5 cm); a 3M, 100 % (200/200) | Necesita 3M pasos: a 1.5M la mitad de las seeds aprende tarde (82.5 %); a 3M hay una sola corrida completa |
| **`suave_bajada` (la de hoy), a 3M** | v69 (3M) | Es la recompensa por defecto, no hay que cambiar nada; 99 % (199/200) y 3.7 cm | La menos suave (Δv pedida 0.119); con desvío 1 depende más de la seed; una sola corrida a 3M |

## Cómo seguir

1. **`cola_pendiente.txt`:** `c003` y `c005` + desvío 0.61 a 3M con 3 seeds (repiten completas v103 y v104). Con eso se
   elige la recompensa y el desvío por defecto (`TODO.md`, punto 1).
2. Probar el desvío 0.37 con `c003` (con `base` subió de 79 a 85 %).
3. Considerar sacar el término de bajada si con desvío 0.61 no suma (comparar `suave_c003` sin bajada contra `c003`).
4. Laboratorio: medir los escalones de velocidad para decidir el PID del simulador.

## Notas

- Huecos de numeración: v43, v44, v48, v49 y v59–v62 se corrieron con el número que tenían reservado desde el 2026-10-15.
  Los demás números sin corrida eran de pruebas descartadas o reservas duplicadas (`BITACORA.md`, 2026-10-25).
- Comparaciones: siempre con ≥ 3 seeds y el modelo final en 100 episodios. Una seed engañó varias veces esta vez también:
  v91 (`c005`, 100 %) parecía la mejor hasta que v92 y v98 aprendieron tarde; v84 (`centro`, 96 %) no se repitió.
