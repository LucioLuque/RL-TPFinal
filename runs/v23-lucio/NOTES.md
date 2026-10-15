# v23-lucio

Cambio: progreso k=3 además de la distancia (`A2_k3`), seed 42

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 1 (seed 42)](../../docs/pruebas-recompensas-2026-10-15.md#tanda-1-seed-42) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `A2_k3` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (71 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 15% / 63% / 76%. Cruza 50 %: 0.62M.
- **Best** (1.4M), 100 episodios: 75% (IC 66–82 %). {'choque_plataforma': 25, 'exito': 75}.
  Δacción 0.86, Δv pedida 0.272 m/s.
- **Final** (1.5M), 100 episodios: 64% (IC 54–73 %). {'choque_plataforma': 33, 'exito': 64, 'tiempo': 2, 'choque_inclinacion': 1}.
  Δacción 0.83, Δv pedida 0.267 m/s.

**Lectura:** Mismo éxito final que base; aprende antes; menos suave.
