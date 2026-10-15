# v28-lucio

Cambio: castigo por estar bajo y afuera de la plataforma (`borde_k1`), seed 42

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 3: castigo por estar bajo y afuera](../../docs/pruebas-recompensas-2026-10-15.md#tanda-3-castigo-por-estar-bajo-y-afuera-seed-42) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `borde_k1` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (60 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 0% / 0%. Cruza 50 %: nunca.
- **Best** (1.5M), 100 episodios: 0% (IC 0–4 %). {'tiempo': 97, 'choque_inclinacion': 3}.
  Δacción 2.37, Δv pedida 0.509 m/s.
- **Final** (1.5M), 100 episodios: 0% (IC 0–4 %). {'tiempo': 96, 'choque_inclinacion': 4}.
  Δacción 2.30, Δv pedida 0.500 m/s.

**Lectura:** Falla: queda flotando (castigar estar bajo hace que no baje nunca).
