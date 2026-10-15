# v41-lucio

Cambio: progreso k=3 además de la distancia (`A2_k3`), seed 3

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 6: seed 3](../../docs/pruebas-recompensas-2026-10-15.md#tanda-6-seed-3) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `A2_k3` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (53 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 0% / 8%. Cruza 50 %: nunca.
- **Best** (0.3M), 100 episodios: 32% (IC 24–42 %). {'tiempo': 28, 'choque_plataforma': 39, 'exito': 32, 'choque_inclinacion': 1}.
  Δacción 0.10, Δv pedida 0.078 m/s.
- **Final** (1.5M), 100 episodios: 55% (IC 45–64 %). {'choque_plataforma': 32, 'exito': 55, 'choque_inclinacion': 9, 'tiempo': 4}.
  Δacción 1.17, Δv pedida 0.265 m/s.

**Lectura:** A2_k3 seed 3: aprende tarde.
