# v53-lucio

Cambio: castigo por bajar estando afuera y cerca del tope (`bajada_k03`), seed 42

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 8: castigar bajar estando afuera](../../docs/pruebas-recompensas-2026-10-15.md#tanda-8-castigar-bajar-estando-afuera-bajada_k03-sola-y-con-suave_c002) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `bajada_k03` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (56 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 0% / 0%. Cruza 50 %: nunca.
- **Best** (1.5M), 100 episodios: 30% (IC 22–40 %). {'choque_inclinacion': 7, 'tiempo': 48, 'exito': 30, 'choque_plataforma': 15}.
  Δacción 1.16, Δv pedida 0.288 m/s.
- **Final** (1.5M), 100 episodios: 26% (IC 18–35 %). {'tiempo': 55, 'choque_plataforma': 11, 'exito': 26, 'choque_inclinacion': 8}.
  Δacción 1.17, Δv pedida 0.284 m/s.

**Lectura:** bajada_k03 sola queda flotando con la seed 42.
