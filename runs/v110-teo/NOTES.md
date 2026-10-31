# v110-teo

Cambio: `suave_bajada_c005` + desvío 0.61 entrenada 3M pasos en vez de 1.5M, seed 3

| | v98-lucio | v110-teo |
|---|---|---|
| Éxito final (100 ep.) | 72% (62–80) | 97% (92–99) |
| Éxito best (100 ep.) | 78% (69–85) | 97% (92–99) |
| Best éxito (8 ep.) | 88% | 100% |
| Best reward | 17.05 | 21.51 |
| Largo ep. (best) | 113.4 | 81.2 |
| Best en timestep | 1,500,000 | 1,700,000 |
| Timesteps totales | 1,500,000 | 3,000,000 |
| Final: cómo terminan | exito 72, choque_plataforma 21, tiempo 6, choque_piso 1 | exito 97, choque_plataforma 2, tiempo 1 |
| Final: centro, mediana / < 5 cm | 13.4 cm / 6% | 4.7 cm / 55% |
| Final: llega a tocar a (mediana) | 0.41 m/s | 0.49 m/s |
| Final: Δacción / Δv pedida (p95) | 0.027 / 0.041 (0.134) m/s | 0.039 / 0.059 (0.160) m/s |
| Final: inclinación RMS / jerk | 8.1° / 23 m/s³ | 6.9° / 31 m/s³ |

## Qué cambió
- Solo la duración: 1.5M → 3M pasos. Misma recompensa (`suave_bajada_c005`), seed (3), exploración
  (`--log_std_init -0.5`) e hiperparámetros que v98. Entre los commits (b2961d0 → 61c0368) solo cambiaron comentarios.
- Repite completa v104-lucio (misma configuración, cortada en 2.95M sin modelo final; su best dio 100 %).
- Entrenada en el laboratorio S004, con 3 corridas en paralelo (ver v105-teo).

## Por qué
`TODO.md`, punto 1: `c003` y `c005` a 3M con 3 seeds para elegir la recompensa final. Esta seed aprendía tarde a
1.5M (v98: 72 %).

## Resultado
- **97 %** (v98 a 1.5M: 72 %): 2 choques contra la plataforma y 1 tiempo agotado. Aprende a ~1.3M (evals de 8
  episodios: 100 % desde 1.3M), antes que v98 en la máquina de Lucio.
- Centra mucho mejor (4.7 contra 13.4 cm). Δv pedida 0.059 m/s: algo menos suave que v108 (0.043).
- Sigue tocando a ~0.5 m/s.

## Próximo paso
- Ver v109-teo (seed 2 quedó flotando) y la seed 4 en la cola.
