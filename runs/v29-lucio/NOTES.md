# v29-lucio

Cambio: recompensa `base`, seed 1

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 4: otras seeds](../../docs/pruebas-recompensas-2026-10-15.md#tanda-4-otras-seeds--base-no-es-robusta) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `base` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (57 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 0% / 0%. Cruza 50 %: nunca.
- **Best** (0.2M), 100 episodios: 10% (IC 6–17 %). {'choque_piso': 64, 'choque_plataforma': 25, 'tiempo': 1, 'exito': 10}.
  Δacción 0.14, Δv pedida 0.101 m/s.
- **Final** (1.5M), 100 episodios: 0% (IC 0–4 %). {'choque_plataforma': 9, 'tiempo': 76, 'choque_inclinacion': 15}.
  Δacción 1.45, Δv pedida 0.334 m/s.

**Lectura:** base con la seed 1 no aprende: queda flotando.
