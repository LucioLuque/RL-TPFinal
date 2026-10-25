# v44-lucio

Cambio: progreso k=1 además de la distancia (`A2_k1`), seed 1: flota

| | v26-lucio | v44-lucio |
|---|---|---|
| Éxito final (100 ep.) | 74% (65–82) | 0% (0–4) |
| Éxito best (100 ep.) | 66% (56–74) | 16% (10–24) |
| Best éxito (8 ep.) | 100% | 25% |
| Best reward | 20.61 | -10.76 |
| Largo ep. (best) | 57.2 | 155.1 |
| Best en timestep | 1,200,000 | 400,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | choque_plataforma 25, exito 74, choque_inclinacion 1 | tiempo 67, choque_plataforma 23, choque_inclinacion 10 |
| Final: centro, mediana / < 5 cm | 5.6 cm / 36% | – |
| Final: llega a tocar a (mediana) | 0.41 m/s | 0.36 m/s |
| Final: Δacción / Δv pedida (p95) | 0.98 / 0.296 (0.676) m/s | 2.42 / 0.456 (0.869) m/s |
| Final: inclinación RMS / jerk | 6.7° / 43 m/s³ | 8.7° / 66 m/s³ |

## Qué cambió
- La misma recompensa que v26 (`A2_k1`: `base` + progreso `1·(d_anterior − d)`), con la seed 1. Desvío por defecto (1).
  Número reservado desde el 2026-10-15.

## Por qué
`A2_k1` tenía una sola seed (v26, s42: 74 %). Completar seeds para el informe.

## Resultado
- **0 % en el modelo final: queda flotando** (67 de 100 episodios por tiempo). Aterrizaba algo hasta 0.4M (hasta 25 % en
  el eval de 8 episodios) y después nunca más.
- La seed 1 con desvío 1 es la difícil: `base` (v29) y `PBRS_k10` (v43) tampoco aprendieron con ella; `A2_k3` (v33) sí,
  recién a 1.4M. Con desvío 0.61, `base` sí aprende con la seed 1 (v50: 79 %).

## Próximo paso
- Seed 2 (v49).
