# v26-lucio

Cambio: progreso k=1 además de la distancia (`A2_k1`), seed 42

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 2: más variantes de progreso](../../docs/pruebas-recompensas-2026-10-15.md#tanda-2-más-variantes-de-progreso-seed-42) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `A2_k1` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (69 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 9% / 66% / 82%. Cruza 50 %: 0.74M.
- **Best** (1.2M), 100 episodios: 66% (IC 56–74 %). {'choque_plataforma': 24, 'choque_piso': 3, 'exito': 66, 'tiempo': 7}.
  Δacción 1.07, Δv pedida 0.309 m/s.
- **Final** (1.5M), 100 episodios: 74% (IC 65–82 %). {'choque_plataforma': 25, 'exito': 74, 'choque_inclinacion': 1}.
  Δacción 0.98, Δv pedida 0.296 m/s.

**Lectura:** Aprende antes que base; final igual a base; menos suave.
