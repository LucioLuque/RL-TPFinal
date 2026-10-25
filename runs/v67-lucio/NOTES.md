# v67-lucio

Cambio: `suave_bajada` con `--log_std_init -0.5` (desvío inicial 0.61), seed 2

| | v63-lucio | v67-lucio |
|---|---|---|
| Éxito final (100 ep.) | 93% (86–97) | 89% (81–94) |
| Éxito best (100 ep.) | 91% (84–95) | 87% (79–92) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 19.60 | 19.10 |
| Largo ep. (best) | 54.1 | 57.1 |
| Best en timestep | 1,500,000 | 1,400,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 93, tiempo 1, choque_inclinacion 2, choque_plataforma 4 | exito 89, choque_plataforma 9, tiempo 2 |
| Final: centro, mediana / < 5 cm | 7.0 cm / 24% | 6.5 cm / 38% |
| Final: toca a (mediana) | 0.18 m/s | 0.03 m/s |
| Final: Δacción / Δv pedida (p95) | 0.30 / 0.152 (0.443) m/s | 0.10 / 0.090 (0.238) m/s |
| Final: inclinación RMS / jerk | 9.2° / 37 m/s³ | 7.7° / 32 m/s³ |


## Qué cambió
- Exploración: `log_std_init` 0 → −0.5 (desvío inicial 1 → 0.61). Misma recompensa, seed (2) e hiperparámetros que
  v63, que es la comparación. `env.py` con los términos nuevos de 2026-10-24 apagados (mismo entorno que v63).

## Por qué
Tercera seed de `suave_bajada` + desvío 0.61 (prioridad 1 de `cola_pendiente.txt`), con v65 (s42) y v66 (s1).

## Resultado
- 89 % en el modelo final contra 93 % de v63: los intervalos se pisan, no es una diferencia.
- Más suave y más centrada: Δv pedida 0.090 m/s contra 0.152 (p95 0.24 contra 0.44), aterriza a 6.5 cm del centro
  (38 % a menos de 5 cm, contra 7.0 cm y 24 %) y toca casi sin velocidad (mediana 0.03 m/s contra 0.18).
- Choca el borde 9 de 100 veces (v63: 4). Evals de 8 episodios: aprende desde 0.6M y oscila entre 75 y 100 % al final.
- **Las 3 seeds juntas** (`compare_runs --by-reward`): éxito final 92 / 97 / 89 % → 93 % de media, contra 92 % de
  `suave_bajada` con desvío 1 (4 seeds). Δv pedida 0.083 contra 0.137 m/s, centro 6.3 contra 8.2 cm, 36 % contra 21 %
  a menos de 5 cm, toca a 0.18 contra 0.28 m/s. La suavidad mejora en 2 de 3 seeds (con la seed 1, v66, no).

## Próximo paso
- Usar el desvío 0.61 como base de las próximas variantes de suavidad (`suave_bajada_c005`, v91–v93).
