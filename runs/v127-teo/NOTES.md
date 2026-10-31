# v127-teo

Cambio: acción como velocidad + premio por tocar despacio (`suave_bajada_c003_vel_tocar`), seed 42

| | v124-teo | v127-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 97% (92–99) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.37 | 25.51 |
| Largo ep. (best) | 53.1 | 49.8 |
| Best en timestep | 2,100,000 | 3,000,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 100 |
| Final: centro, mediana / < 5 cm | 3.7 cm / 71% | 3.7 cm / 74% |
| Final: llega a tocar a (mediana, m/s) | 0.51 | 0.33 |
| Final: Δacción / Δv pedida (p95) | 0.058 / 0.068 (0.163) m/s | 0.110 / 0.105 (0.273) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.0° / 31 | 6.7° / 28 |

## Qué cambió
- **Premio por tocar despacio** (`landing_vz_coef: 10`, `env.py`): al aterrizar se suma `10·(1 − v_toque/0.6)`, donde
  `v_toque` es la velocidad de bajada relativa a la plataforma en el primer contacto. Se paga una vez y solo si
  aterriza, así que no cambia nada antes de tocar (no debería causar la trampa de flotar).
- Variante `suave_bajada_c003_vel_tocar` en `rewards.yaml`: `suave_bajada_c003_vel` + `landing_vz_coef: 10`. Es lo
  mismo que `suave_bajada_c003_tocar` (v111–v113), pero con la acción como velocidad.
- Mismo resto que v124-teo (acción como velocidad, seed 42, desvío 0.61, 3M). Laboratorio S004, 3 corridas en paralelo.
- `Δacción` incluye la salida `s`, que en este modo no se usa: comparar con `Δv pedida` (ver v124-teo).

## Por qué
Con la acción de dirección, el premio terminal casi no frenaba (v111–v113: 0.43–0.47 m/s) porque `s` está saturado
en 1. Con la acción como velocidad, frenar es achicar `dz`.

## Resultado
- 100 %, y **es la primera política que frena claramente al tocar: 0.33 m/s de mediana (p90 0.43)**, contra 0.51 de
  v124 y 0.43 de v111 (`c003_tocar`, misma seed). La siguiente más lenta del proyecto es v17-lucio (0.38 m/s); con efecto suelo, v115–v117 tocan a
  0.38–0.41.
- Es menos suave en el resto del vuelo: Δv pedida 0.105 contra 0.068 m/s de v124. Centra igual (3.7 cm, 74 % a menos
  de 5 cm).
- `dz` sigue saturado en el 70 % de los pasos (v124: 78 %): frena solo cerca del tope.
- Aprende rápido (50 % a 0.50M) y está en 8 de 8 de forma estable desde 1.9M.

## Próximo paso
- Ver v129, que junta las 3 seeds.
