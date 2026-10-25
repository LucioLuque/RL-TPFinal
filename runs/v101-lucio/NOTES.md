# v101-lucio

Cambio: castigo a la acción 0.03 (`suave_bajada_c003`) con desvío inicial 0.61, seed 42

| | v65-lucio | v101-lucio |
|---|---|---|
| Éxito final (100 ep.) | 92% (85–96) | 95% (89–98) |
| Éxito best (100 ep.) | 89% (81–94) | 96% (90–98) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 18.73 | 19.87 |
| Largo ep. (best) | 59.4 | 52.6 |
| Best en timestep | 1,500,000 | 1,400,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 92, tiempo 1, choque_plataforma 7 | choque_plataforma 3, tiempo 2, exito 95 |
| Final: centro, mediana / < 5 cm | 5.2 cm / 42% | 5.4 cm / 42% |
| Final: llega a tocar a (mediana) | 0.47 m/s | 0.45 m/s |
| Final: Δacción / Δv pedida (p95) | 0.04 / 0.059 (0.159) m/s | 0.06 / 0.073 (0.182) m/s |
| Final: inclinación RMS / jerk | 7.7° / 28 m/s³ | 7.5° / 31 m/s³ |

## Qué cambió
- Lo mismo que v99, con la seed 42. Se compara con v65 (`suave_bajada` + desvío 0.61, seed 42) y v91 (castigo 0.05,
  seed 42: 100 %, Δv pedida 0.051).

## Por qué
Segunda seed de `suave_bajada_c003`.

## Resultado
- **95 % en el modelo final** (v65: 92 %; intervalos que se pisan). Aprende a tiempo: 100 % en los evals de 8 episodios
  desde 1.0M.
- **No es más suave que v65 con esta seed:** Δv pedida 0.073 contra 0.059 m/s. Centro igual (5.4 contra 5.2 cm).
- Con dos seeds (99 % y 95 %), `c003` es tan robusta como el castigo 0.02; la suavidad extra depende de la seed
  (seed 1: 0.083 contra 0.100; seed 42: 0.073 contra 0.059).

## Próximo paso
- Seed 2 (v102) para cerrar las 3.
