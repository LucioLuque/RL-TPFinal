# v51-lucio

Cambio: recompensa `base`, `--log_std_init -0.5` (desvío inicial 0.61), seed 2

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 7: control de exploración](../../docs/pruebas-recompensas-2026-10-15.md#tanda-7-control--base-con-menos-ruido-de-exploración-sin-tocar-la-recompensa) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `base` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (60 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 3% / 1% / 71%. Cruza 50 %: 1.22M.
- **Best** (1.2M), 100 episodios: 72% (IC 62–80 %). {'exito': 72, 'choque_plataforma': 26, 'choque_inclinacion': 2}.
  Δacción 0.36, Δv pedida 0.166 m/s.
- **Final** (1.5M), 100 episodios: 76% (IC 67–83 %). {'exito': 76, 'tiempo': 1, 'choque_plataforma': 23}.
  Δacción 0.36, Δv pedida 0.179 m/s.

**Lectura:** Control: base con desvío inicial 0.61, seed 2.
