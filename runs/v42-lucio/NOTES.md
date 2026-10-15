# v42-lucio

Cambio: castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 3

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 6: seed 3](../../docs/pruebas-recompensas-2026-10-15.md#tanda-6-seed-3) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `suave_c002` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (75 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 32% / 60% / 73%. Cruza 50 %: 0.55M.
- **Best** (1.5M), 100 episodios: 74% (IC 65–82 %). {'choque_plataforma': 22, 'choque_piso': 3, 'exito': 74, 'tiempo': 1}.
  Δacción 0.17, Δv pedida 0.098 m/s.
- **Final** (1.5M), 100 episodios: 71% (IC 62–79 %). {'choque_plataforma': 25, 'choque_piso': 3, 'exito': 71, 'tiempo': 1}.
  Δacción 0.15, Δv pedida 0.093 m/s.

**Lectura:** suave_c002 seed 3.
