# v56-lucio

Cambio: castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 1

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 8: castigar bajar estando afuera](../../docs/pruebas-recompensas-2026-10-15.md#tanda-8-castigar-bajar-estando-afuera-bajada_k03-sola-y-con-suave_c002) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `suave_bajada` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (74 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 62% / 84%. Cruza 50 %: 0.69M.
- **Best** (1.5M), 100 episodios: 84% (IC 76–90 %). {'choque_plataforma': 13, 'choque_piso': 1, 'exito': 84, 'tiempo': 1, 'choque_inclinacion': 1}.
  Δacción 0.13, Δv pedida 0.093 m/s.
- **Final** (1.5M), 100 episodios: 88% (IC 80–93 %). {'choque_plataforma': 9, 'choque_piso': 1, 'exito': 88, 'tiempo': 2}.
  Δacción 0.13, Δv pedida 0.091 m/s.

**Lectura:** suave_bajada seed 1: 88 %.
