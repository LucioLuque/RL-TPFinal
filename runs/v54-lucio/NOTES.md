# v54-lucio

Cambio: castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 42

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 8: castigar bajar estando afuera](../../docs/pruebas-recompensas-2026-10-15.md#tanda-8-castigar-bajar-estando-afuera-bajada_k03-sola-y-con-suave_c002) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `suave_bajada` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (75 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 65% / 92%. Cruza 50 %: 0.68M.
- **Best** (1.5M), 100 episodios: 89% (IC 81–94 %). {'exito': 89, 'choque_plataforma': 9, 'tiempo': 1, 'choque_inclinacion': 1}.
  Δacción 0.14, Δv pedida 0.100 m/s.
- **Final** (1.5M), 100 episodios: 92% (IC 85–96 %). {'exito': 92, 'choque_plataforma': 5, 'choque_inclinacion': 1, 'tiempo': 2}.
  Δacción 0.13, Δv pedida 0.100 m/s.

**Lectura:** suave_bajada seed 42: 92 %, la que menos choca el borde.
