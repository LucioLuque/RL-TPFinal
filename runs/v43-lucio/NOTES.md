# v43-lucio

Cambio: shaping por potencial k=10 sumado a `base` (`PBRS_k10`), seed 1: flota

| | v25-lucio | v43-lucio |
|---|---|---|
| Éxito final (100 ep.) | 72% (62–80) | 1% (0–5) |
| Éxito best (100 ep.) | 69% (59–77) | 20% (13–29) |
| Best éxito (8 ep.) | 88% | 25% |
| Best reward | 27.83 | 2.25 |
| Largo ep. (best) | 72.0 | 224.2 |
| Best en timestep | 1,500,000 | 100,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 72, choque_plataforma 24, tiempo 3, choque_inclinacion 1 | choque_plataforma 16, tiempo 78, choque_inclinacion 5, exito 1 |
| Final: centro, mediana / < 5 cm | 8.6 cm / 17% | 9.1 cm / 0% |
| Final: llega a tocar a (mediana) | 0.40 m/s | 0.38 m/s |
| Final: Δacción / Δv pedida (p95) | 1.47 / 0.358 (0.781) m/s | 1.03 / 0.305 (0.661) m/s |
| Final: inclinación RMS / jerk | 6.7° / 46 m/s³ | 9.6° / 77 m/s³ |

## Qué cambió
- La misma recompensa que v25 (`PBRS_k10`: `base` + `γ·Φ(s') − Φ(s)` con `Φ = −10·d`), con la seed 1. Mismos
  hiperparámetros y desvío por defecto (1). Número reservado desde el 2026-10-15.

## Por qué
`PBRS_k10` tenía una sola seed (v25, s42: 72 %, aprendiendo recién a partir de 1.2M). Completar seeds para el informe.

## Resultado
- **1 % en el modelo final: queda flotando** (78 de 100 episodios por tiempo). Aterrizaba algo al principio (25 % en el
  eval de 8 episodios a 0.1M) y desde 0.4M nunca más: la trampa de flotar.
- Es lo que se esperaba de la teoría (`BITACORA.md`, 2026-10-15): el PBRS cancela en promedio el `−0.1·d` por paso y el
  agente pierde el apuro por terminar. Con la seed 42 salió de la trampa a 1.2M; con la 1, no en 1.5M.

## Próximo paso
- Seed 2 (v48).
