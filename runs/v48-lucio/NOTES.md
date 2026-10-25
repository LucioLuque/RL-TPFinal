# v48-lucio

Cambio: shaping por potencial k=10 sumado a `base` (`PBRS_k10`), seed 2: flota

| | v25-lucio | v48-lucio |
|---|---|---|
| Éxito final (100 ep.) | 72% (62–80) | 3% (1–8) |
| Éxito best (100 ep.) | 69% (59–77) | 0% (0–4) |
| Best éxito (8 ep.) | 88% | 12% |
| Best reward | 27.83 | 3.73 |
| Largo ep. (best) | 72.0 | 368.6 |
| Best en timestep | 1,500,000 | 1,300,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 72, choque_plataforma 24, tiempo 3, choque_inclinacion 1 | choque_plataforma 32, tiempo 51, choque_inclinacion 14, exito 3 |
| Final: centro, mediana / < 5 cm | 8.6 cm / 17% | 13.4 cm / 0% |
| Final: llega a tocar a (mediana) | 0.40 m/s | 0.39 m/s |
| Final: Δacción / Δv pedida (p95) | 1.47 / 0.358 (0.781) m/s | 1.04 / 0.269 (0.604) m/s |
| Final: inclinación RMS / jerk | 6.7° / 46 m/s³ | 10.2° / 78 m/s³ |

## Qué cambió
- La misma recompensa que v25 y v43 (`PBRS_k10`), con la seed 2. Número reservado desde el 2026-10-15.

## Por qué
Tercera seed de `PBRS_k10`.

## Resultado
- **3 % en el modelo final**: 51 de 100 episodios por tiempo y el resto choques. Evals de 8 episodios en 0 % salvo uno
  (12 % a 1.3M): no salió de la trampa de flotar en 1.5M.
- **Las 3 seeds de `PBRS_k10`: 72 / 1 / 3 % → 25 %** (s42 / s1 / s2). Solo la seed 42 (v25) salió de la trampa, y recién
  a 1.2M. El PBRS, aunque no cambia la política óptima, saca el apuro por terminar y con 1.5M pasos casi nunca aprende.
  Es de las peores recompensas probadas; la conclusión de 2026-10-15 ("PBRS aprende tarde") era optimista por usar
  una sola seed.

## Próximo paso
- Nada con PBRS.
