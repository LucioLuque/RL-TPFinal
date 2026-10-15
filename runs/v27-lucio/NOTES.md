# v27-lucio

Cambio: progreso k=3 que mide solo lo que se movió el dron (`A2_k3_drone`), seed 42

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 2: más variantes de progreso](../../docs/pruebas-recompensas-2026-10-15.md#tanda-2-más-variantes-de-progreso-seed-42) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `A2_k3_drone` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (54 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 0% / 1%. Cruza 50 %: nunca.
- **Best** (0.2M), 100 episodios: 35% (IC 26–45 %). {'tiempo': 14, 'choque_plataforma': 48, 'exito': 35, 'choque_piso': 2, 'choque_inclinacion': 1}.
  Δacción 0.11, Δv pedida 0.088 m/s.
- **Final** (1.5M), 100 episodios: 2% (IC 1–7 %). {'tiempo': 86, 'choque_plataforma': 11, 'exito': 2, 'choque_inclinacion': 1}.
  Δacción 3.11, Δv pedida 0.555 m/s.

**Lectura:** Falla: aprende a perseguir la plataforma sin bajar (el progreso sin la plataforma no es telescópico).
