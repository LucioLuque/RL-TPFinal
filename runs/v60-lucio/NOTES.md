# v60-lucio

Cambio: recompensa `base` con `--log_std_init -1.0` (desvío inicial 0.37), seed 42

| | v52-lucio | v60-lucio |
|---|---|---|
| Éxito final (100 ep.) | 81% (72–88) | 78% (69–85) |
| Éxito best (100 ep.) | 73% (64–81) | 79% (70–86) |
| Best éxito (8 ep.) | 88% | 100% |
| Best reward | 16.48 | 17.84 |
| Largo ep. (best) | 58.4 | 55.1 |
| Best en timestep | 900,000 | 1,400,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 81, choque_plataforma 16, choque_inclinacion 1, tiempo 2 | choque_plataforma 21, exito 78, tiempo 1 |
| Final: centro, mediana / < 5 cm | 4.7 cm / 54% | 8.3 cm / 20% |
| Final: llega a tocar a (mediana) | 0.47 m/s | 0.42 m/s |
| Final: Δacción / Δv pedida (p95) | 0.33 / 0.186 (0.425) m/s | 0.23 / 0.170 (0.400) m/s |
| Final: inclinación RMS / jerk | 7.4° / 42 m/s³ | 8.1° / 44 m/s³ |

## Qué cambió
- Exploración: `log_std_init` −0.5 → −1.0 (desvío inicial 0.61 → 0.37). Misma recompensa (`base`), seed (42) e
  hiperparámetros que v52, que es la comparación (y v21: `base` con desvío 1, 72 %).
- Número reservado desde la sesión del 2026-10-15 (`BITACORA.md`, 2026-10-25, "Huecos de numeración").

## Por qué
Con `base`, bajar el desvío de 1 a 0.61 hizo que aprenda en todas las seeds (v50–v52). ¿Todavía menos ruido ayuda más?

## Resultado
- **78 % en el modelo final** contra 81 % de v52 (intervalos que se pisan). Menos centrada (8.3 contra 4.7 cm) y
  parecida en suavidad (Δv pedida 0.170 contra 0.186 m/s).
- **Aprende más tarde y de forma irregular:** evals de 8 episodios entre 0 y 50 % hasta 1.3M (100 % recién a 1.4M); v52
  cruzaba el 50 % en el entrenamiento a 0.78M. Con tan poco ruido explora menos.
- Una seed: faltan v61 y v62.

## Próximo paso
- Seeds 1 y 2 (v61, v62).
