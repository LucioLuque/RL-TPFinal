# v98-lucio

Cambio: castigo a la acción 0.05 (`suave_bajada_c005`) con desvío inicial 0.61, seed 3

| | v64-lucio | v98-lucio |
|---|---|---|
| Éxito final (100 ep.) | 95% (89–98) | 72% (62–80) |
| Éxito best (100 ep.) | 88% (80–93) | 78% (69–85) |
| Best éxito (8 ep.) | 100% | 88% |
| Best reward | 18.26 | 17.05 |
| Largo ep. (best) | 59.1 | 113.4 |
| Best en timestep | 1,400,000 | 1,500,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 95, choque_plataforma 5 | exito 72, choque_plataforma 21, tiempo 6, choque_piso 1 |
| Final: centro, mediana / < 5 cm | 8.3 cm / 18% | 13.4 cm / 6% |
| Final: llega a tocar a (mediana) | 0.42 m/s | 0.41 m/s |
| Final: Δacción / Δv pedida (p95) | 0.50 / 0.204 (0.559) m/s | 0.03 / 0.041 (0.134) m/s |
| Final: inclinación RMS / jerk | 8.9° / 41 m/s³ | 8.1° / 23 m/s³ |

## Qué cambió
- Lo mismo que v91–v93, con la seed 3. Se compara con v64 (`suave_bajada`, seed 3; no hay `suave_bajada` + desvío 0.61
  con la seed 3).

## Por qué
Cuarta seed de `suave_bajada_c005`, porque la seed 1 (v92) aprendió tarde.

## Resultado
- **72 % en el modelo final** (v64: 95 %). Como v92, aprende tarde: evals de 8 episodios en 0 % hasta 1.0M y 88 % recién
  a 1.4–1.5M; a 1.5M todavía está aprendiendo. Choca el borde 21 de 100 veces y aterriza lejos del centro (13.4 cm).
- Muy suave (Δv pedida 0.041 m/s), como todas las de `c005`.
- **Las 4 seeds de `c005` + desvío 0.61: 100 / 61 / 97 / 72 % → 82.5 % de media; 2 de 4 aprenden tarde.** Con el
  castigo a la acción 0.05, a 1.5M pasos, no es robusta.

## Próximo paso
- Si se quiere esta suavidad, entrenarla más pasos (3M) para que las seeds lentas terminen de aprender, o probar 0.03.
