# v40-lucio

Cambio: recompensa `base`, seed 3

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 6: seed 3](../../docs/pruebas-recompensas-2026-10-15.md#tanda-6-seed-3) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `base` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (69 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 7% / 68% / 75%. Cruza 50 %: 0.72M.
- **Best** (1.5M), 100 episodios: 74% (IC 65–82 %). {'choque_plataforma': 22, 'choque_piso': 3, 'exito': 74, 'choque_inclinacion': 1}.
  Δacción 0.70, Δv pedida 0.243 m/s.
- **Final** (1.5M), 100 episodios: 70% (IC 60–78 %). {'choque_plataforma': 25, 'choque_piso': 3, 'exito': 70, 'tiempo': 1, 'choque_inclinacion': 1}.
  Δacción 0.71, Δv pedida 0.240 m/s.

**Lectura:** base seed 3.
