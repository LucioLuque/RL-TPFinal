# v58-lucio

Cambio: castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), `--log_std_init -0.5` (desvío inicial 0.61), seed 1

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 9: más seeds de suave_bajada](../../docs/pruebas-recompensas-2026-10-15.md#tanda-9-más-seeds-de-suave_bajada-y-suave_c002-con-menos-ruido-de-exploración) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `suave_c002` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (65 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 9% / 68% / 86%. Cruza 50 %: 0.70M.
- **Best** (1.3M), 100 episodios: 81% (IC 72–88 %). {'choque_plataforma': 17, 'exito': 81, 'choque_piso': 2}.
  Δacción 0.08, Δv pedida 0.085 m/s.
- **Final** (1.5M), 100 episodios: 85% (IC 77–91 %). {'choque_plataforma': 12, 'exito': 85, 'tiempo': 2, 'choque_piso': 1}.
  Δacción 0.07, Δv pedida 0.079 m/s.

**Lectura:** suave_c002 + desvío 0.61, seed 1: 85 %.
