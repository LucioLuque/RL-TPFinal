# v52-lucio

Cambio: recompensa `base`, `--log_std_init -0.5` (desvío inicial 0.61), seed 42

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 7: control de exploración](../../docs/pruebas-recompensas-2026-10-15.md#tanda-7-control--base-con-menos-ruido-de-exploración-sin-tocar-la-recompensa) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `base` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (67 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 12% / 61% / 86%. Cruza 50 %: 0.78M.
- **Best** (0.9M), 100 episodios: 73% (IC 64–81 %). {'exito': 73, 'choque_plataforma': 23, 'choque_piso': 1, 'choque_inclinacion': 1, 'tiempo': 2}.
  Δacción 0.23, Δv pedida 0.160 m/s.
- **Final** (1.5M), 100 episodios: 81% (IC 72–88 %). {'exito': 81, 'choque_plataforma': 16, 'choque_inclinacion': 1, 'tiempo': 2}.
  Δacción 0.33, Δv pedida 0.186 m/s.

**Lectura:** Control: base con desvío inicial 0.61, seed 42.
