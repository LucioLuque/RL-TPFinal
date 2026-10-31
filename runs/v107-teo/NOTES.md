# v107-teo

Cambio: `suave_bajada_c003` + desvío 0.61 entrenada 3M pasos en vez de 1.5M, seed 2

| | v102-lucio | v107-teo |
|---|---|---|
| Éxito final (100 ep.) | 99% (95–100) | 100% (96–100) |
| Éxito best (100 ep.) | 98% (93–99) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 19.42 | 21.51 |
| Largo ep. (best) | 57.6 | 50.2 |
| Best en timestep | 1,400,000 | 2,700,000 |
| Timesteps totales | 1,500,000 | 3,000,000 |
| Final: cómo terminan | exito 99, choque_plataforma 1 | exito 100 |
| Final: centro, mediana / < 5 cm | 7.2 cm / 35% | 3.7 cm / 65% |
| Final: llega a tocar a (mediana) | 0.47 m/s | 0.49 m/s |
| Final: Δacción / Δv pedida (p95) | 0.077 / 0.086 (0.216) m/s | 0.039 / 0.063 (0.145) m/s |
| Final: inclinación RMS / jerk | 7.5° / 33 m/s³ | 7.3° / 30 m/s³ |

## Qué cambió
- Solo la duración: 1.5M → 3M pasos. Misma recompensa (`suave_bajada_c003`), seed (2), exploración
  (`--log_std_init -0.5`) e hiperparámetros que v102. Entre los commits (00374d5 → 61c0368) solo cambiaron
  comentarios.
- Entrenada en el laboratorio S004, con 3 corridas en paralelo (ver v105-teo).

## Por qué
`TODO.md`, punto 1: `c003` y `c005` a 3M con 3 seeds para elegir la recompensa final.

## Resultado
- **100 % en el modelo final** (v102 a 1.5M: 99 %).
- La que más mejora en centrado de las tres seeds: 3.7 cm de mediana y 65 % a menos de 5 cm (v102: 7.2 cm, 35 %).
  Δv pedida 0.063 contra 0.086 m/s.
- Evals de 8 episodios: 100 % desde 1.6M (un bajón a 75 % a 1.3M).
- Sigue tocando a ~0.5 m/s.

## Próximo paso
- Ver v105-teo: juntar las 3 seeds y comparar con `c005` a 3M.
