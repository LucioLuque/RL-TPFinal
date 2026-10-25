# v93-lucio

Cambio: castigo a la acción 0.05 (`suave_bajada_c005`) con desvío inicial 0.61, seed 2

| | v63-lucio | v93-lucio |
|---|---|---|
| Éxito final (100 ep.) | 93% (86–97) | 97% (92–99) |
| Éxito best (100 ep.) | 91% (84–95) | 95% (89–98) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 19.60 | 21.14 |
| Largo ep. (best) | 54.1 | 57.8 |
| Best en timestep | 1,500,000 | 1,400,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 93, tiempo 1, choque_inclinacion 2, choque_plataforma 4 | exito 97, tiempo 1, choque_plataforma 2 |
| Final: centro, mediana / < 5 cm | 7.0 cm / 24% | 6.3 cm / 39% |
| Final: llega a tocar a (mediana) | 0.43 m/s | 0.49 m/s |
| Final: Δacción / Δv pedida (p95) | 0.30 / 0.152 (0.443) m/s | 0.04 / 0.059 (0.154) m/s |
| Final: inclinación RMS / jerk | 9.2° / 37 m/s³ | 7.6° / 29 m/s³ |

## Qué cambió
- Lo mismo que v91, con la seed 2. Se compara con v63 (`suave_bajada`, seed 2; la tabla) y v67 (`suave_bajada` +
  desvío 0.61, seed 2: 89 %, Δv pedida 0.090 m/s, 6.5 cm).

## Por qué
Tercera seed de `suave_bajada_c005`.

## Resultado
- **97 % en el modelo final** (v63: 93 %, v67: 89 %; intervalos que se pisan). 2 choques contra el borde.
- Más suave que las dos: Δv pedida 0.059 m/s (v63: 0.152; v67: 0.090) y más centrada: 6.3 cm, 39 % a menos de 5 cm.
- Evals de 8 episodios: aprende desde 0.7M, más o menos como v67.
- Las 3 seeds de `c005` + desvío 0.61: 100 / 61 / 97 % → 86 % de media, contra 93 % de `suave_bajada` + desvío 0.61.
  Las que aprenden son las más suaves y centradas del proyecto; la seed 1 aprende tarde.

## Próximo paso
- Seed 3 (v98).
