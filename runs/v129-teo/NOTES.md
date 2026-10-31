# v129-teo

Cambio: acción como velocidad + premio por tocar despacio (`suave_bajada_c003_vel_tocar`), seed 2

| | v126-teo | v129-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 99% (95–100) |
| Éxito best (100 ep.) | 100% (96–100) | 97% (92–99) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.02 | 22.91 |
| Largo ep. (best) | 50.9 | 54.1 |
| Best en timestep | 2,800,000 | 2,100,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 99, choque_inclinacion 1 |
| Final: centro, mediana / < 5 cm | 5.1 cm / 46% | 4.7 cm / 58% |
| Final: llega a tocar a (mediana, m/s) | 0.50 | 0.46 |
| Final: Δacción / Δv pedida (p95) | 0.140 / 0.096 (0.230) m/s | 0.066 / 0.075 (0.184) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.0° / 34 | 6.9° / 31 |

## Qué cambió
- Lo mismo que v127-teo (acción como velocidad + `landing_vz_coef: 10`), con la seed 2. Mismo resto que v126-teo.
  Laboratorio S004, 3 corridas en paralelo.

## Por qué
Tercera seed de `suave_bajada_c003_vel_tocar` (ver v127-teo).

## Resultado
- 99 % (1 choque contra la plataforma). Más suave que v126 (Δv pedida 0.075 contra 0.096 m/s).
- **Casi no frena:** toca a 0.46 m/s (p90 0.57), contra 0.50 de v126.
- **Con 3 seeds** (v127–v129): 100 / 100 / 99 %; tocan a **0.33** / 0.45 / 0.46 m/s, contra 0.51 / 0.48 / 0.50 sin el
  premio (v124–v126) y 0.43 / 0.47 / 0.45 con el premio y la acción de dirección (v111–v113). **Con la acción como
  velocidad, frenar se puede aprender, pero lo descubre 1 seed de 3.**
- Hipótesis: la exploración casi no prueba valores intermedios de `dz`, porque la media de la gaussiana de `dz` está en
  ~1.6–1.9, muy afuera de [−1, 1]: casi todo lo que se explora sigue saturado. Además, el premio por frenar es chico: pasar de 0.5 a
  0.33 m/s suma ~2.8, contra ~23 por aterrizar.

## Próximo paso
- **Curriculum desde v127** (`train.py --init_from v127-teo`) con más premio por tocar despacio (`landing_vz_coef` 25).
- La misma variante con `landing_vz_coef` 25 desde cero, con 3 seeds.
- Castigar que la media de la gaussiana se salga de [−1, 1] (*bounds loss*, como `bounds_loss_coef` de rl_games), para
  que la exploración pruebe velocidades intermedias.
