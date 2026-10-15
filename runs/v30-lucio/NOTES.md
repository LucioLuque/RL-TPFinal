# v30-lucio

Cambio: recompensa `base`, seed 2

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 4: otras seeds](../../docs/pruebas-recompensas-2026-10-15.md#tanda-4-otras-seeds--base-no-es-robusta) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `base` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (70 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 8% / 52% / 75%. Cruza 50 %: 0.87M.
- **Best** (1.2M), 100 episodios: 74% (IC 65–82 %). {'choque_plataforma': 22, 'choque_piso': 3, 'exito': 74, 'tiempo': 1}.
  Δacción 0.35, Δv pedida 0.163 m/s.
- **Final** (1.5M), 100 episodios: 76% (IC 67–83 %). {'choque_plataforma': 20, 'choque_piso': 4, 'exito': 76}.
  Δacción 0.39, Δv pedida 0.183 m/s.

**Lectura:** base con la seed 2 aprende como la seed 42.
