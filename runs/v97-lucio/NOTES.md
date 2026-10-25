# v97-lucio

Cambio: castigo a la acción 0.1 (`suave_bajada_c01`) con desvío inicial 0.61, seed 1

| | v66-lucio | v97-lucio |
|---|---|---|
| Éxito final (100 ep.) | 97% (92–99) | 42% (33–52) |
| Éxito best (100 ep.) | 96% (90–98) | 40% (31–50) |
| Best éxito (8 ep.) | 100% | 50% |
| Best reward | 18.13 | -0.50 |
| Largo ep. (best) | 56.8 | 69.2 |
| Best en timestep | 1,500,000 | 1,500,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 97, choque_plataforma 2, tiempo 1 | choque_plataforma 42, choque_piso 5, exito 42, tiempo 9, choque_inclinacion 2 |
| Final: centro, mediana / < 5 cm | 7.1 cm / 28% | 13.8 cm / 10% |
| Final: llega a tocar a (mediana) | 0.46 m/s | 0.35 m/s |
| Final: Δacción / Δv pedida (p95) | 0.11 / 0.100 (0.271) m/s | 0.04 / 0.031 (0.144) m/s |
| Final: inclinación RMS / jerk | 7.8° / 32 m/s³ | 8.3° / 23 m/s³ |

## Qué cambió
- Lo mismo que v96, con la seed 1. Se compara con v66 (`suave_bajada` + desvío 0.61, seed 1).

## Por qué
Segunda seed de `suave_bajada_c01`.

## Resultado
- **42 %** (v66: 97 %): empieza a aprender recién a 1.2M (evals de 8 episodios 0 / 12 / 0 / 12 / 50 % al final). Choca
  el borde 42 de 100 veces y aterriza lejos del centro (13.8 cm).
- Con v96 (0 %), `suave_bajada_c01` queda descartada: un castigo a la acción de 0.1 frena el aprendizaje.

## Próximo paso
- Nada con 0.1. Si se busca más suavidad, probar 0.03 o seguir entrenando `c005` más pasos.
