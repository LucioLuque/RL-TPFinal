# v63-lucio

Cambio: castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 2

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 9: más seeds de suave_bajada](../../docs/pruebas-recompensas-2026-10-15.md#tanda-9-más-seeds-de-suave_bajada-y-suave_c002-con-menos-ruido-de-exploración) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `suave_bajada` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (71 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 62% / 86%. Cruza 50 %: 0.70M.
- **Best** (1.5M), 100 episodios: 91% (IC 84–95 %). {'exito': 91, 'choque_plataforma': 5, 'choque_inclinacion': 2, 'tiempo': 2}.
  Δacción 0.29, Δv pedida 0.149 m/s.
- **Final** (1.5M), 100 episodios: 93% (IC 86–97 %). {'exito': 93, 'tiempo': 1, 'choque_inclinacion': 2, 'choque_plataforma': 4}.
  Δacción 0.30, Δv pedida 0.152 m/s.

**Lectura:** suave_bajada seed 2: 93 %.
