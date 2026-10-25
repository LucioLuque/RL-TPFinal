# v49-lucio

Cambio: progreso k=1 además de la distancia (`A2_k1`), seed 2

| | v26-lucio | v49-lucio |
|---|---|---|
| Éxito final (100 ep.) | 74% (65–82) | 72% (62–80) |
| Éxito best (100 ep.) | 66% (56–74) | 70% (60–78) |
| Best éxito (8 ep.) | 100% | 75% |
| Best reward | 20.61 | 11.76 |
| Largo ep. (best) | 57.2 | 52.1 |
| Best en timestep | 1,200,000 | 1,500,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | choque_plataforma 25, exito 74, choque_inclinacion 1 | choque_plataforma 25, choque_piso 2, exito 72, tiempo 1 |
| Final: centro, mediana / < 5 cm | 5.6 cm / 36% | 8.7 cm / 33% |
| Final: llega a tocar a (mediana) | 0.41 m/s | 0.40 m/s |
| Final: Δacción / Δv pedida (p95) | 0.98 / 0.296 (0.676) m/s | 1.41 / 0.358 (0.736) m/s |
| Final: inclinación RMS / jerk | 6.7° / 43 m/s³ | 6.4° / 45 m/s³ |

## Qué cambió
- La misma recompensa que v26 y v44 (`A2_k1`), con la seed 2. Número reservado desde el 2026-10-15.

## Por qué
Tercera seed de `A2_k1`.

## Resultado
- **72 % en el modelo final** (v26, seed 42: 74 %). Choca el borde 25 de 100 veces, como `base`. Poco suave (Δv pedida
  0.358 m/s).
- Aprende algo al principio (hasta 50 % a 0.4M), lo pierde entre 0.5M y 1.1M, y vuelve a 62–75 % al final.
- **Las 3 seeds de `A2_k1`: 74 / 0 / 72 % → 49 %**, el mismo patrón que `base` con desvío 1 (72 / 0 / 76 %): el progreso
  con k = 1 no cambia nada respecto de `base`.

## Próximo paso
- Nada con `A2_k1`.
