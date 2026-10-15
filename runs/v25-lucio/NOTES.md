# v25-lucio

Cambio: shaping por potencial k=10 sumado a `base` (`PBRS_k10`), seed 42

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 1 (seed 42)](../../docs/pruebas-recompensas-2026-10-15.md#tanda-1-seed-42) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `PBRS_k10` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (57 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 0% / 0% / 70%. Cruza 50 %: 1.31M.
- **Best** (1.5M), 100 episodios: 69% (IC 59–77 %). {'choque_plataforma': 30, 'exito': 69, 'choque_inclinacion': 1}.
  Δacción 1.46, Δv pedida 0.360 m/s.
- **Final** (1.5M), 100 episodios: 72% (IC 62–80 %). {'exito': 72, 'choque_plataforma': 24, 'tiempo': 3, 'choque_inclinacion': 1}.
  Δacción 1.47, Δv pedida 0.358 m/s.

**Lectura:** Flota hasta 1.2M y después aprende de golpe; la más brusca.
