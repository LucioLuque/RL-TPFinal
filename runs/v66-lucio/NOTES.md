# v66-lucio

Cambio: `suave_bajada` con `--log_std_init -0.5` (desvío inicial 0.61), seed 1

| | v56-lucio | v66-lucio |
|---|---|---|
| Éxito final (100 ep.) | 88% (80–93) | 97% (92–99) |
| Éxito best (100 ep.) | 84% (76–90) | 96% (90–98) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 18.14 | 18.13 |
| Largo ep. (best) | 61.1 | 56.8 |
| Best en timestep | 1,500,000 | 1,500,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | choque_plataforma 9, choque_piso 1, exito 88, tiempo 2 | exito 97, choque_plataforma 2, tiempo 1 |
| Final: centro, mediana / < 5 cm | 9.6 cm / 18% | 7.1 cm / 28% |
| Final: llega a tocar a (mediana) | 0.42 m/s | 0.46 m/s |
| Final: Δacción / Δv pedida (p95) | 0.13 / 0.091 (0.280) m/s | 0.11 / 0.100 (0.271) m/s |
| Final: inclinación RMS / jerk | 8.1° / 30 m/s³ | 7.8° / 32 m/s³ |


## Qué cambió
- Exploración: `log_std_init` 0 → −0.5 (desvío inicial de la acción 1 → 0.61). Misma recompensa (`suave_bajada`), misma seed (1) y mismos hiperparámetros que v56-lucio; `env.py` idéntico.
- Se compara con v56-lucio, la misma recompensa y seed con el desvío por defecto (no con la corrida anterior en número).

## Por qué
Prioridad 1 de `cola_pendiente.txt` (`docs/pruebas-recompensas-2026-10-15.md`, "Cómo seguir"): bajar el ruido de exploración se sumó al castigo a la acción en `suave_c002` (v57, v58); faltaba probarlo con `suave_bajada`.

## Resultado
- **97 % en el modelo final, contra 88 % de v56** (intervalos 92–99 y 80–93: casi no se pisan). Choca el borde 2 de
  100 veces (v56: 9) y llega a tocar a la misma velocidad (0.46 contra 0.42 m/s).
- **No es más suave en vuelo:** Δv pedida 0.100 m/s contra 0.091 de v56; centrado algo mejor (7.1 contra 9.6 cm).
  La mejora de suavidad de v65 (seed 42) no se repite con esta seed.
- Aprende más tarde que v56 (cruza 50 % a 0.99M contra 0.69M) y sigue subiendo al final.

## Próximo paso
- Seed 2 (v67) para cerrar las 3 seeds.

_Corregido el 2026-10-25: la velocidad al tocar se mide ahora en el último paso antes del contacto (antes, al final del paso con contacto, cuando el choque ya había frenado al dron)._
