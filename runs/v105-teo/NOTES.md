# v105-teo

Cambio: `suave_bajada_c003` + desvío 0.61 entrenada 3M pasos en vez de 1.5M, seed 42

| | v101-lucio | v105-teo |
|---|---|---|
| Éxito final (100 ep.) | 95% (89–98) | 100% (96–100) |
| Éxito best (100 ep.) | 96% (90–98) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 19.87 | 20.61 |
| Largo ep. (best) | 52.6 | 58.0 |
| Best en timestep | 1,400,000 | 3,000,000 |
| Timesteps totales | 1,500,000 | 3,000,000 |
| Final: cómo terminan | exito 95, choque_plataforma 3, tiempo 2 | exito 100 |
| Final: centro, mediana / < 5 cm | 5.4 cm / 42% | 4.1 cm / 60% |
| Final: llega a tocar a (mediana) | 0.45 m/s | 0.51 m/s |
| Final: Δacción / Δv pedida (p95) | 0.058 / 0.073 (0.182) m/s | 0.034 / 0.063 (0.154) m/s |
| Final: inclinación RMS / jerk | 7.5° / 31 m/s³ | 6.9° / 31 m/s³ |

## Qué cambió
- Solo la duración: 1.5M → 3M pasos. Misma recompensa (`suave_bajada_c003`), seed (42), exploración
  (`--log_std_init -0.5`) e hiperparámetros que v101. Entre los commits (00374d5 → 61c0368) solo cambiaron
  comentarios; el `diff.patch` es solo `cola_pendiente.txt`.
- Primera corrida entrenada en el laboratorio S004 de la universidad (`docs/laboratorio-s004-ssh.md`), con
  `tools/run_queue.py --parallel 3`: 3M pasos en ~32 min (~1800 pasos/s por corrida, con 3 a la vez).
- Repite completa v103-lucio (misma configuración, cortada en 2.81M sin modelo final).

## Por qué
`TODO.md`, punto 1: comparar las candidatas `c003` y `c005` a 3M con 3 seeds para elegir la recompensa final. A
1.5M las diferencias entre recompensas eran sobre todo de velocidad de aprendizaje (`BITACORA.md`, 2026-10-25).

## Resultado
- **100 % en el modelo final** (v101 a 1.5M: 95 %), sin choques.
- Más centrada (4.1 cm de mediana, 60 % a menos de 5 cm, contra 5.4 cm y 42 %) y un poco más suave (Δv pedida 0.063
  contra 0.073 m/s). Igual que con `suave_bajada` (v69) y `c005` (v100): **entrenar más centra**.
- Sigue llegando a tocar casi a la velocidad máxima de bajada (0.51 m/s).
- Evals de 8 episodios: aprende a ~1.3M (100 %) y queda en 100 % desde 1.9M.
- `wx` y `wy` se recortan en ~0.7 % de los pasos (`OBS_ANG_VEL_SCALE`, `TODO.md`, punto 3).

## Próximo paso
- Juntar con las otras seeds (v106, v107) y comparar con `c005` a 3M (v108–v110, v100):
  `python -m tools.compare_runs v105-teo v106-teo v107-teo v108-teo v109-teo v110-teo --by-reward`.
- Tocar suave: `suave_bajada_c003_tocar` (premio terminal por tocar despacio).
