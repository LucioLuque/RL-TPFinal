# v87-lucio

Cambio: premio al aterrizar 25 − 100·d_xy (`suave_bajada_centro`), seed 1

| | v56-lucio | v87-lucio |
|---|---|---|
| Éxito final (100 ep.) | 88% (80–93) | 83% (75–89) |
| Éxito best (100 ep.) | 84% (76–90) | 85% (77–91) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 18.14 | 15.98 |
| Largo ep. (best) | 61.1 | 53.4 |
| Best en timestep | 1,500,000 | 1,500,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | choque_plataforma 9, choque_piso 1, exito 88, tiempo 2 | choque_plataforma 10, exito 83, choque_inclinacion 4, tiempo 3 |
| Final: centro, mediana / < 5 cm | 9.6 cm / 18% | 8.0 cm / 23% |
| Final: llega a tocar a (mediana) | 0.42 m/s | 0.42 m/s |
| Final: Δacción / Δv pedida (p95) | 0.13 / 0.091 (0.280) m/s | 0.17 / 0.109 (0.331) m/s |
| Final: inclinación RMS / jerk | 8.1° / 30 m/s³ | 9.1° / 32 m/s³ |

## Qué cambió
- Lo mismo que v84 (`landing_dxy_coef` 50 → 100), con la seed 1. Se compara con v56 (`suave_bajada`, seed 1).

## Por qué
Segunda seed de `suave_bajada_centro`, después de v84 (seed 42: 96 %, más suave, pero no más centrada).

## Resultado
- 83 % en el modelo final contra 88 % de v56 (intervalos que se pisan). No repite el 96 % de v84.
- Centra apenas mejor que v56 (8.0 contra 9.6 cm de mediana) y es algo menos suave (Δv pedida 0.109 contra 0.091).
- Evals de 8 episodios: aprende desde 0.6M, como v56, y oscila entre 62 y 100 % al final.
- Con dos seeds (96 % y 83 %), `suave_bajada_centro` no muestra una mejora clara sobre `suave_bajada` ni en éxito ni
  en centrado.

## Próximo paso
- Seed 2 (v90) para cerrar; y la versión con desvío 0.61 (v94, v95), que es donde más centró `suave_bajada`.
