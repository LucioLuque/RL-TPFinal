# v55-lucio

Cambio: castigo por bajar estando afuera y cerca del tope (`bajada_k03`), seed 1

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 8: castigar bajar estando afuera](../../docs/pruebas-recompensas-2026-10-15.md#tanda-8-castigar-bajar-estando-afuera-bajada_k03-sola-y-con-suave_c002) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `bajada_k03` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (60 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 0% / 81%. Cruza 50 %: 1.23M.
- **Best** (1.5M), 100 episodios: 77% (IC 68–84 %). {'exito': 77, 'choque_plataforma': 19, 'tiempo': 4}.
  Δacción 0.53, Δv pedida 0.183 m/s.
- **Final** (1.5M), 100 episodios: 81% (IC 72–88 %). {'exito': 81, 'choque_plataforma': 18, 'tiempo': 1}.
  Δacción 0.55, Δv pedida 0.186 m/s.

**Lectura:** bajada_k03 sola con la seed 1 aprende, tarde.
