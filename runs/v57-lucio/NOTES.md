# v57-lucio

Cambio: castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), `--log_std_init -0.5` (desvío inicial 0.61), seed 42

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 9: más seeds de suave_bajada](../../docs/pruebas-recompensas-2026-10-15.md#tanda-9-más-seeds-de-suave_bajada-y-suave_c002-con-menos-ruido-de-exploración) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `suave_c002` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (72 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 29% / 78% / 93%. Cruza 50 %: 0.54M.
- **Best** (0.9M), 100 episodios: 75% (IC 66–82 %). {'exito': 75, 'choque_plataforma': 22, 'choque_piso': 1, 'tiempo': 2}.
  Δacción 0.05, Δv pedida 0.066 m/s.
- **Final** (1.5M), 100 episodios: 93% (IC 86–97 %). {'exito': 93, 'choque_plataforma': 4, 'tiempo': 3}.
  Δacción 0.09, Δv pedida 0.088 m/s.

**Lectura:** suave_c002 + desvío 0.61: 93 %, la más suave.
