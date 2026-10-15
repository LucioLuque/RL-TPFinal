# v64-lucio

Cambio: castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 3

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 9: más seeds de suave_bajada](../../docs/pruebas-recompensas-2026-10-15.md#tanda-9-más-seeds-de-suave_bajada-y-suave_c002-con-menos-ruido-de-exploración) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `suave_bajada` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (73 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 60% / 88%. Cruza 50 %: 0.70M.
- **Best** (1.4M), 100 episodios: 88% (IC 80–93 %). {'exito': 88, 'choque_plataforma': 9, 'choque_inclinacion': 3}.
  Δacción 0.41, Δv pedida 0.179 m/s.
- **Final** (1.5M), 100 episodios: 95% (IC 89–98 %). {'exito': 95, 'choque_plataforma': 5}.
  Δacción 0.50, Δv pedida 0.204 m/s.

**Lectura:** suave_bajada seed 3: 95 %.
