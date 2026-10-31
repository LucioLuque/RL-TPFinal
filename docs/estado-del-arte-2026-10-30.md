# Estado del arte: tocar suave, acciones suaves, efecto suelo y lo que falta modelar (2026-10-30)

Búsqueda bibliográfica de la noche del 2026-10-30 (teo, sesión de Claude), mientras se entrenaba en el laboratorio
S004. Lo que se probó esa noche (v105–v135) dice **[probado]**, con el resultado; el detalle está en `BITACORA.md`
(2026-10-30) y en las `NOTES.md` de cada corrida. Lo que no se probó está en `TODO.md`.

## El problema

- **Tocar suave:** todas las políticas llegan a tocar bajando a 0.41–0.50 m/s, casi la velocidad máxima de 0.6
  (`touchdown.vz_median` en `eval_*.json`). Bajan con `dz` saturado en 60–97 % de los pasos (bang-bang).
- **Acciones suaves:** el castigo por cambiar la acción (`reward_action_coef`, `c003` y `c005`) bajó el cambio de la
  velocidad pedida de ~0.14 a ~0.05–0.07 m/s por paso. Más castigo aprende más lento (0.1 no aprende).
- **La trampa de flotar:** todo castigo **por paso** que encarezca acercarse o bajar cerca del tope (A1, B, XY,
  `borde_k1`, `suave_bajada_v01`, `_flare`) dejó al dron flotando. No es que el óptimo cambie: con `_flare`,
  aterrizar seguía valiendo mucho más (≈ −2.5 de castigo contra +25). Es un problema de **exploración**: al principio
  el dron casi nunca aterriza, cobra el castigo muchas veces antes de descubrir el +25, y PPO aprende a evitar la
  zona. De ahí sale un criterio para elegir ideas: **que no cambien los retornos cerca del tope durante la
  exploración**, o que lo hagan solo cuando el dron ya sabe aterrizar.

## 1. Tocar suave

| Idea | Qué es | Trampa de flotar | Estado |
|---|---|---|---|
| **Premio terminal por tocar despacio** | Al aterrizar, `+k·(1 − v_toque/0.6)`. Se paga una vez y solo si aterriza. | No: no cambia nada antes de aterrizar | **[probado]** `landing_vz_coef: 10`. Con la acción de siempre casi no frena (v111–v113: 0.43–0.47 m/s); con la acción como velocidad, 1 seed de 3 frena (v127: 0.33 m/s). |
| **Curriculum** | Entrenar a aterrizar y después seguir con el término de tocar suave (`_flare`) o con más castigo a la acción. Kooi y Babuška (2021) aterrizan un Crazyflie real en una plataforma inclinada con PPO + curriculum; Goldschmid y Ahmad (2024) aterrizan en plataformas móviles con un curriculum por etapas. | No, si el término entra cuando ya aterriza | `train.py --init_from <run> --reward <otra>` arranca una corrida nueva desde el modelo final de otra (`--load` sigue la misma corrida y pisa su `model.zip`). Sin probar: el siguiente paso es seguir v127 con más premio (`TODO.md`). |
| **Perfil de bajada (tau)** | La teoría tau (Lee; Alkowatly et al. 2015, en un cuadricóptero real) frena con τ̇ constante, donde τ = h / v_bajada, y llega con velocidad casi nula. Se puede usar como referencia `v_ref(h)` y premiar seguirla. | Sí, si se premia o castiga por paso cerca del tope. Con PBRS no cambia el óptimo, pero tampoco hace frenar. | Idea. Si se hace, que sea con curriculum. |
| **Controlador híbrido** | RL para alinearse con la plataforma y una ley fija para los últimos centímetros (`vz = −k·h` con un mínimo). Es lo más seguro para el robot real. | No aplica | Idea. Cambia la acción en el tramo final: revisar `SIM2REAL.md`. |

**Resultado de esa noche: el premio terminal casi no frena** (v111–v113: 100 % de éxito, toque a 0.45 m/s de mediana
contra 0.50 de `c003`). La causa es la acción, no la recompensa. La acción de gym-pybullet-drones es
`v = 0.6·s·dir/|dir|`, y en todas las políticas `s` está saturado en 1 en el 100 % de los pasos (media de la gaussiana
~3, `tools/action_saturation.py`). **El dron va siempre a 0.6 m/s**: para bajar más lento tiene que inclinar la
dirección hacia los costados, y con media 3 y desvío ~0.6 la exploración casi nunca prueba `s < 1`. Por eso ni
castigar (`_flare`) ni premiar (`_tocar`) le enseñan a frenar, y por eso la salida de la trampa de `c005` y `_v01` es
`s = 0`.

**[probado]** La acción como velocidad (`action_mode: velocity`, `v = 0.6·(dx, dy, dz)`):
- sin el premio (`suave_bajada_c003_vel`, v124–v126): aprende antes (50 % a ~0.5M contra ~0.7M), pero es menos suave
  (Δv pedida 0.087 contra 0.066 m/s) y **toca igual a 0.5 m/s**: poder frenar no alcanza si nada lo pide;
- con el premio (`suave_bajada_c003_vel_tocar`, v127–v129): **v127 toca a 0.33 m/s** (p90 0.43), la más lenta del
  proyecto; las otras dos seeds, a 0.45–0.46. Frenar se puede aprender, pero lo descubre 1 seed de 3. Hipótesis: la
  media de la gaussiana de `dz` está en ~1.6–1.9, así que la exploración casi no prueba velocidades intermedias.
  Siguientes pruebas en `TODO.md`: curriculum desde v127, más premio y castigar que la media salga de [−1, 1].

En la literatura de aterrizaje en plataformas móviles con RL (Rodriguez-Ramos et al. 2019; Lander.AI 2024; Goldschmid y
Ahmad 2024), la recompensa castiga la velocidad relativa o el exceso de velocidad al bajar. No encontré un trabajo
con cuadricóptero que use un premio terminal por la velocidad de toque, así que esa prueba es propia.

## 2. Acciones suaves sin tocar la recompensa

La idea común es sacar la suavidad de la recompensa y ponerla en la **pérdida de la política** o en la
**exploración**. Así no cambia qué estados convienen, y no puede aparecer la trampa de flotar.

| Idea | Qué es | Estado |
|---|---|---|
| **CAPS** (Mysore et al., ICRA 2021) | Dos términos en la pérdida de PPO: temporal, `‖π(s_t) − π(s_{t+1})‖²`, y espacial, `‖π(s) − π(s + ruido)‖²`. Probado en un cuadricóptero real: 80 % menos de consumo y 90 % más de suavidad, con el mismo seguimiento. | **[probado]** `caps.py` (`--caps_temporal 0.01 --caps_spatial 0.01`, v121–v123): 100 %, el mejor centrado del proyecto (2.7–3.8 cm), pero solo ~12 % más suave. Hipótesis: actúa sobre la media sin recortar, muy afuera de [−1, 1]. Probar sobre la media recortada o con más peso. |
| **gSDE** (Raffin et al., CoRL 2021) | El ruido de exploración depende del estado y se sortea cada `n` pasos, así que la exploración no da tirones. En SB3 es `use_sde=True`. | **[probado]** `--use_sde --sde_sample_freq 4 --log_std_init -2` (v118–v120; valores típicos de rl-baselines3-zoo, sin ajustar): 100 %, ~15 % más suave y algo más centrada. |
| **Lipschitz-Constrained Policies** (Chen et al. 2024) | Penaliza el gradiente de la acción respecto de la observación. Reemplaza los castigos de suavidad y los filtros pasa-bajos en humanoides reales. | Idea, parecida a la parte espacial de CAPS. |
| Ruido coloreado en PPO (2023) | Ruido de exploración correlacionado en el tiempo. | Idea, la misma familia que gSDE. |
| Acción como velocidad | `v = 0.6·(dx, dy, dz)` en vez de `0.6·s·dir/|dir|`: frenar es achicar la acción. | **[probado]** `action_mode: velocity` (ver sección 1): menos suave que la acción de siempre. Para el dron real es la misma interfaz: una velocidad pedida de hasta 0.6 m/s. |
| Filtro pasa-bajos o acción incremental | La red pide un cambio de velocidad, o la acción pasa por un filtro antes de ir al dron. | Cambia la acción: después de medir el dron real (`TODO.md`). |

## 3. Efecto suelo

**Qué es.** Cerca de una superficie, el aire que empujan las hélices rebota y el empuje aumenta. El modelo clásico
(Cheeseman y Bennett, 1955) es `T_cerca / T_lejos = 1 / (1 − (R/4z)²)`, con R el radio de la hélice (23 mm en el
CF2X) y z la altura. Además:
- **Efecto suelo parcial** (Sanchez-Cuevas et al. 2017; Herz et al. 2026): si solo algunas hélices están sobre la
  superficie, como cuando el dron pasa por el borde de la plataforma, empujan distinto y el dron se inclina. Es
  justo nuestro caso al aterrizar cerca del borde.
- **No es estacionario:** los modelos suponen flujo estacionario, y cerca del suelo no lo es. Neural-Lander (Shi et
  al. 2019) aprende el residuo con una red y aterriza más suave que un PD.

**Cómo estaba en la simulación.** El entorno usaba `Physics.PYB`, sin efecto suelo, sin drag y sin downwash.
gym-pybullet-drones trae `Physics.PYB_GND` (`BaseAviary._groundEffect`), pero mide la altura contra el piso (z = 0),
y el tope de la plataforma está a 0.35 m: ahí casi no empuja.

**Qué se implementó** (`env.py`, `ground_effect: true`, apagado por defecto): el mismo modelo de la librería
(Shi et al. 2019: `KF·rpm²·11.37·(R/4h)²` por hélice), pero cada hélice mide su altura contra el tope si está encima
de la plataforma, y contra el piso si no. En hover:

| Altura sobre el tope | Empuje extra (% del peso) |
|---|---|
| 10 cm | 4 % |
| 5 cm | 15 % |
| ≤ 3.8 cm (recorte de la librería) | 27 % |
| 3 cm, en el borde (2 hélices adentro y 2 afuera) | 13.5 %, y además inclina |

Con la política de v101 (`c003`, entrenada sin efecto suelo), en 20 episodios: sigue aterrizando (20/20) y toca más
despacio (0.40 contra 0.49 m/s), porque el colchón de aire la frena.

**[probado]** Entrenar con efecto suelo (v115–v117, `suave_bajada_c003_gnd`): aprende igual (100 / 99 / 98 %), pero 2 de 3 seeds tardan más
(50 % recién a ~1.1–1.3M, contra ~0.7M sin efecto suelo). Prueba cruzada: las políticas entrenadas con y sin efecto suelo aterrizan 50/50 con el
efecto ×0, ×0.3, ×1 y ×1.5; solo baja la velocidad de toque (de 0.50 a ~0.35 m/s con ×1.5). Con este modelo, el
efecto suelo amortigua y no compromete el aterrizaje.

**La magnitud es dudosa.** Mediciones en un Crazyflie 2.0 (trabajo de control adaptativo por modelo de referencia,
MRAC) dan **~5 % a 2 radios (4.6 cm)**, con un aumento lineal al acercarse. El modelo de la librería da ~18 % a esa
altura, y Cheeseman-Bennett ~1.6 %. Puede haber un factor 3 o más de diferencia. Además, el Crazyflie real corre su
controlador a ~500 Hz y compensa parte del efecto como si fuera una perturbación; nuestro PID a 24 Hz casi no lo
hace.

**Cómo medirlo en el laboratorio:** hacer hover a 2, 4, 6, 10 y 20 cm sobre el tope del turtlebot quieto, registrar
el empuje que pide el controlador (log del firmware) y ajustar `ground_effect_scale` para que la simulación coincida.
Mientras no esté medido, lo más robusto es **aleatorizar `ground_effect_scale`** entre episodios (por ejemplo entre 0 y
1.5), para que la política aguante cualquier valor. Falta implementarlo.

## 4. Otras variables reales que todavía no se modelan

Revisar contra `SIM2REAL.md` (`~/Documents/Tesis/Laboratorio`), que ya cubre: giro de la plataforma, efecto suelo,
observación de OptiTrack, frecuencias y PID a 24 Hz, aceleración del turtlebot y domain randomization. Lo que sigue
puede estar ahí o no.

| Variable | Por qué importa | Qué dice la literatura | Cómo meterla |
|---|---|---|---|
| **Latencia** (OptiTrack → PC → radio → Crazyflie) | A 24 Hz, un retardo de 1–2 pasos cambia mucho el control cerca del tope | E2E-Fly y otros: es de los riesgos más grandes del sim2real, y conviene compensarla o aleatorizarla | Cola de acciones con un retardo de 0–2 pasos, sorteado por episodio |
| **Dinámica de los motores** | `PYB` aplica las RPM pedidas de inmediato | Constante de tiempo ~0.035 s; SimpleFlight (Crazyflie 2.1): la transferencia casi no depende de ella | Baja prioridad |
| **Masa e inercia** (marcadores de OptiTrack, batería) | Cambia el empuje para hover | Molchanov et al. 2019: aleatorizar ±20 % alrededor del valor nominal ayuda; más, empeora | Aleatorizar `M` y `J` por episodio |
| **Batería** | Al bajar la tensión, baja el empuje máximo | Trabajos de 2026 modelan la caída de tensión en el Crazyflie | Aleatorizar `KF` o el empuje máximo ±10 % |
| **Drag y downwash** | Rozamiento del aire a velocidad; el aire que rebota en la plataforma | `Physics.PYB_GND_DRAG_DW` en gym-pybullet-drones | Probar `PYB_GND_DRAG_DW` con nuestro efecto suelo |
| **Ruido de la observación** | La posición de OptiTrack es precisa, pero la velocidad sale de derivar y tiene ruido | | Ruido gaussiano en velocidad y ángulos |
| **Rebote y fricción en el tope** | El material del turtlebot define si el dron rebota o resbala al tocar | | Ajustar restitución y fricción del tope en PyBullet |
| **Viento o corrientes de aire** | Aire acondicionado del laboratorio | | Fuerza aleatoria chica, constante por episodio |

## 5. Orden propuesto

Actualizado con los resultados del 2026-10-30:

1. **Tocar suave:** seguir v127 (acción como velocidad + premio por tocar) con curriculum y más premio, y castigar que
   la media de la gaussiana se salga de [−1, 1] para que la exploración pruebe velocidades intermedias.
2. **Suavidad:** CAPS y gSDE suavizan poco tal como están; probar CAPS sobre la media recortada o con más peso.
3. **Efecto suelo:** medir en el laboratorio y aleatorizar `ground_effect_scale`.
4. **Latencia y masa:** aleatorizarlas, después de medir.

## Fuentes

- Mysore et al. 2021, *Regularizing Action Policies for Smooth Control with RL* (CAPS): https://ai.bu.edu/caps/index.html, https://arxiv.org/abs/2012.06644
- Raffin, Kober y Stulp 2021, *Smooth Exploration for Robotic RL* (gSDE): https://arxiv.org/abs/2005.05719
- Chen et al. 2024, *Learning Smooth Humanoid Locomotion through Lipschitz-Constrained Policies*: https://arxiv.org/abs/2410.11825
- *Colored Noise in PPO* 2023: https://arxiv.org/pdf/2312.11091
- Kooi y Babuška 2021, *Inclined Quadrotor Landing using Deep RL*: https://arxiv.org/abs/2103.09043, código: https://github.com/Jacobkooi/InclinedDroneLander
- Goldschmid y Ahmad 2024, *RL based Autonomous Multi-Rotor Landing on Moving Platforms*: https://arxiv.org/abs/2302.13192
- Polvara et al. 2018, *Autonomous Quadrotor Landing using Deep RL*: https://arxiv.org/html/1709.03339
- *Lander.AI* 2024: https://arxiv.org/pdf/2403.06572
- Aterrizaje en plataformas móviles con movimiento incierto (visión + DRL): https://www.researchgate.net/publication/402130417
- Aterrizaje suave planetario con DRL (recompensa de seguimiento de velocidad): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8662435/
- Teoría tau para aterrizar: https://pcwww.liv.ac.uk/eweb/fst/publications/AIAA%20GNC%202005-6404.pdf, https://www.mdpi.com/2079-9292/8/2/184, https://publications.aston.ac.uk/id/eprint/39701
- Shi et al. 2019, *Neural Lander*: https://arxiv.org/abs/1811.08027
- Sanchez-Cuevas et al. 2017, efecto suelo parcial: https://idus.us.es/handle/11441/94910, https://zenodo.org/records/3647908/files/Multirotor%20aerodynamic%20effects%20close%20to%20obstacles-preprint.pdf
- Caprace et al. 2023 (NASA), rotor sobre un borde: https://ntrs.nasa.gov/api/citations/20230007525/downloads/Aviation2023_Caprace.pdf
- Herz et al. 2026, bordes parciales: https://saemobilus.sae.org/papers/effects-partial-boundaries-variable-wind-conditions-a-free-flying-multirotor-platform-f-0082-2026-0091
- Efecto suelo medido en un Crazyflie 2.0 (MRAC): https://www.researchgate.net/publication/334522861
- Modelo cuasi-estacionario de efecto suelo para multirrotores: https://www.researchgate.net/publication/345755241
- Efecto techo con hélices del tamaño del Crazyflie: https://climb.mie.utoronto.ca/pdfs/hsiao2018ceiling.pdf
- CrazySim (simulador con efecto suelo): https://github.com/gtfactslab/CrazySim
- Eschmann et al. 2023, *Learning to Fly in Seconds*: https://arxiv.org/abs/2311.13081
- Molchanov et al. 2019, *Sim-to-(Multi)-Real*: https://whoenig.github.io/publications/2019_IROS_Molchanov_Chen.pdf
- SimpleFlight / *What Matters in Learning a Zero-Shot Sim-to-Real RL Policy for Quadrotor Control?*: https://arxiv.org/pdf/2412.11764, https://sites.google.com/view/simpleflight/
- E2E-Fly: https://arxiv.org/pdf/2604.12916
- RL para cuadricópteros consciente de la batería: https://arxiv.org/html/2609.37316v1
- MuJoCo-Drones-Gym: https://arxiv.org/pdf/2606.08039
