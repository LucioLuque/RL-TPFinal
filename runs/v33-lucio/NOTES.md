# v33-lucio

Cambio: progreso k=3 además de la distancia (`A2_k3`), seed 1

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 4: otras seeds](../../docs/pruebas-recompensas-2026-10-15.md#tanda-4-otras-seeds--base-no-es-robusta) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `A2_k3` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (57 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 0% / 62%. Cruza 50 %: 1.40M.
- **Best** (1.4M), 100 episodios: 64% (IC 54–73 %). {'choque_plataforma': 31, 'exito': 64, 'tiempo': 3, 'choque_inclinacion': 2}.
  Δacción 1.36, Δv pedida 0.292 m/s.
- **Final** (1.5M), 100 episodios: 64% (IC 54–73 %). {'choque_plataforma': 28, 'tiempo': 8, 'exito': 64}.
  Δacción 1.51, Δv pedida 0.352 m/s.

**Lectura:** A2_k3 con la seed 1 sí aprende, tarde (1.4M).
