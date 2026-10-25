# v65-lucio

Cambio: `suave_bajada` con `--log_std_init -0.5` (desvío inicial 0.61), seed 42

| | v54-lucio | v65-lucio |
|---|---|---|
| Éxito final (100 ep.) | 92% (85–96) | 92% (85–96) |
| Éxito best (100 ep.) | 89% (81–94) | 89% (81–94) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 19.14 | 18.73 |
| Largo ep. (best) | 51.1 | 59.4 |
| Best en timestep | 1,500,000 | 1,500,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 92, choque_plataforma 5, choque_inclinacion 1, tiempo 2 | exito 92, tiempo 1, choque_plataforma 7 |
| Final: centro, mediana / < 5 cm | 8.1 cm / 24% | 5.2 cm / 42% |
| Final: llega a tocar a (mediana) | 0.45 m/s | 0.47 m/s |
| Final: Δacción / Δv pedida (p95) | 0.13 / 0.100 (0.288) m/s | 0.04 / 0.059 (0.159) m/s |
| Final: inclinación RMS / jerk | 8.1° / 32 m/s³ | 7.7° / 28 m/s³ |


## Qué cambió
- Exploración: `log_std_init` 0 → −0.5 (desvío inicial de la acción 1 → 0.61). Misma recompensa (`suave_bajada`), misma seed (42) y mismos hiperparámetros que v54-lucio; `env.py` idéntico.
- Se compara con v54-lucio, la misma recompensa y seed con el desvío por defecto (no con la corrida anterior en número).

## Por qué
Prioridad 1 de `cola_pendiente.txt` (`docs/pruebas-recompensas-2026-10-15.md`, "Cómo seguir"): bajar el ruido de exploración se sumó al castigo a la acción en `suave_c002` (v57, v58); faltaba probarlo con `suave_bajada`.

## Resultado
- Mismo éxito que v54 en el modelo final (92 %, intervalos iguales), pero **más suave y más centrado**: la velocidad
  pedida cambia 0.059 m/s por paso contra 0.100 (p95 0.16 contra 0.29) y aterriza a 5.2 cm del centro (mediana)
  contra 8.1, con 42 % a menos de 5 cm contra 24 %. Llega a tocar igual de rápido (0.47 contra 0.45 m/s).
- Aprende más tarde: cruza 50 % a 0.99M (v54: 0.68M). Evals de 8 episodios: 0 hasta 0.6M, 88 % a 1.2M, 100 % a 1.5M:
  sigue subiendo al final.
- Choca el borde 7 de 100 veces (v54: 5); con 100 episodios eso no es una diferencia.

## Próximo paso
- Ver las seeds 1 y 2 (v66, v67) antes de concluir: la mejora en suavidad puede depender de la seed.
- Si se confirma, combinar el desvío 0.61 con los términos nuevos (`suave_bajada_v01`, `_flare`, `_centro`).

_Corregido el 2026-10-25: la velocidad al tocar se mide ahora en el último paso antes del contacto (antes, al final del paso con contacto, cuando el choque ya había frenado al dron)._
