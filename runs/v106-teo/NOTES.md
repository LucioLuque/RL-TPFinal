# v106-teo

Cambio: `suave_bajada_c003` + desvío 0.61 entrenada 3M pasos en vez de 1.5M, seed 1

| | v99-lucio | v106-teo |
|---|---|---|
| Éxito final (100 ep.) | 99% (95–100) | 100% (96–100) |
| Éxito best (100 ep.) | 91% (84–95) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 20.09 | 21.39 |
| Largo ep. (best) | 44.6 | 46.9 |
| Best en timestep | 1,100,000 | 2,900,000 |
| Timesteps totales | 1,500,000 | 3,000,000 |
| Final: cómo terminan | exito 99, choque_inclinacion 1 | exito 100 |
| Final: centro, mediana / < 5 cm | 6.1 cm / 36% | 4.5 cm / 54% |
| Final: llega a tocar a (mediana) | 0.48 m/s | 0.50 m/s |
| Final: Δacción / Δv pedida (p95) | 0.074 / 0.083 (0.213) m/s | 0.050 / 0.072 (0.173) m/s |
| Final: inclinación RMS / jerk | 7.6° / 31 m/s³ | 7.4° / 31 m/s³ |

## Qué cambió
- Solo la duración: 1.5M → 3M pasos. Misma recompensa (`suave_bajada_c003`), seed (1), exploración
  (`--log_std_init -0.5`) e hiperparámetros que v99. Entre los commits (62c1d87 → 61c0368) no cambió el código de
  entrenamiento.
- Entrenada en el laboratorio S004, con 3 corridas en paralelo (ver v105-teo).

## Por qué
`TODO.md`, punto 1: `c003` y `c005` a 3M con 3 seeds para elegir la recompensa final.

## Resultado
- **100 % en el modelo final** (v99 a 1.5M: 99 %); el best a 1.5M daba 91 %, ahora 100 %.
- Más centrada (4.5 contra 6.1 cm) y algo más suave (Δv pedida 0.072 contra 0.083 m/s).
- Evals de 8 episodios: aprende más tarde que la seed 42 (50 % a 1.0M, 100 % desde 1.6M).
- Sigue tocando a ~0.5 m/s.

## Próximo paso
- Ver v105-teo: juntar las 3 seeds y comparar con `c005` a 3M.
