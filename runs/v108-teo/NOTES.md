# v108-teo

Cambio: `suave_bajada_c005` + desvío 0.61 entrenada 3M pasos en vez de 1.5M, seed 42

| | v91-lucio | v108-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 97% (92–99) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 20.80 | 22.38 |
| Largo ep. (best) | 54.2 | 51.5 |
| Best en timestep | 1,100,000 | 2,900,000 |
| Timesteps totales | 1,500,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 100 |
| Final: centro, mediana / < 5 cm | 5.1 cm / 49% | 3.3 cm / 80% |
| Final: llega a tocar a (mediana) | 0.50 m/s | 0.52 m/s |
| Final: Δacción / Δv pedida (p95) | 0.022 / 0.051 (0.123) m/s | 0.020 / 0.043 (0.104) m/s |
| Final: inclinación RMS / jerk | 7.5° / 29 m/s³ | 7.5° / 28 m/s³ |

## Qué cambió
- Solo la duración: 1.5M → 3M pasos. Misma recompensa (`suave_bajada_c005`), seed (42), exploración
  (`--log_std_init -0.5`) e hiperparámetros que v91. Entre los commits (5f234d6 → 61c0368) solo cambiaron comentarios.
- Entrenada en el laboratorio S004, con 3 corridas en paralelo (ver v105-teo).

## Por qué
`TODO.md`, punto 1: `c003` y `c005` a 3M con 3 seeds para elegir la recompensa final.

## Resultado
- 100 %, igual que a 1.5M. **La política más centrada y más suave del proyecto:** 3.3 cm de mediana y **80 % a menos
  de 5 cm**; Δv pedida 0.043 m/s (p95 0.104). `c003` a 3M (v105–v107): 3.7–4.5 cm y 0.063–0.072 m/s.
- Evals de 8 episodios: 100 % desde 1.6M.
- Sigue tocando a ~0.5 m/s: el castigo a la acción no frena la llegada.

## Próximo paso
- Ver v109-teo: con la seed 2, `c005` quedó flotando. Se agregó la seed 4 a la cola para decidir.
