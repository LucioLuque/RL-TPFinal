# v92-lucio

Cambio: castigo a la acción 0.05 (`suave_bajada_c005`) con desvío inicial 0.61, seed 1

| | v56-lucio | v92-lucio |
|---|---|---|
| Éxito final (100 ep.) | 88% (80–93) | 61% (51–70) |
| Éxito best (100 ep.) | 84% (76–90) | 42% (33–52) |
| Best éxito (8 ep.) | 100% | 62% |
| Best reward | 18.14 | 8.84 |
| Largo ep. (best) | 61.1 | 121.5 |
| Best en timestep | 1,500,000 | 1,400,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | choque_plataforma 9, choque_piso 1, exito 88, tiempo 2 | choque_plataforma 29, exito 61, tiempo 6, choque_inclinacion 4 |
| Final: centro, mediana / < 5 cm | 9.6 cm / 18% | 12.3 cm / 10% |
| Final: llega a tocar a (mediana) | 0.42 m/s | 0.40 m/s |
| Final: Δacción / Δv pedida (p95) | 0.13 / 0.091 (0.280) m/s | 0.04 / 0.044 (0.152) m/s |
| Final: inclinación RMS / jerk | 8.1° / 30 m/s³ | 8.6° / 24 m/s³ |

## Qué cambió
- Lo mismo que v91 (`reward_action_coef` 0.05, `--log_std_init -0.5`), con la seed 1. Se compara con v66
  (`suave_bajada` + desvío 0.61, seed 1) y v56 (`suave_bajada`, seed 1); la tabla es contra v56.

## Por qué
Segunda seed de `suave_bajada_c005`, después del 100 % de v91 (seed 42).

## Resultado
- **Aprende muy tarde: 61 % en el modelo final** (v66: 97 %, v56: 88 %). Los evals de 8 episodios dan 0 % hasta 1.2M,
  y después 12 / 62 / 50 %: a 1.5M todavía está aprendiendo. Falla sobre todo contra el borde (29 de 100).
- Muy suave (Δv pedida 0.044 m/s) pero poco centrada (12.3 cm): es una política que todavía no terminó de aprender.
- **El castigo a la acción más fuerte retrasa el aprendizaje según la seed**; con la seed 42 (v91) no se notó.

## Próximo paso
- Seed 3 (v98) para ver qué tan seguido pasa. Probar más pasos (3M) con esta recompensa, o un castigo intermedio (0.03).
