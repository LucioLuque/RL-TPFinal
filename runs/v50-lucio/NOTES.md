# v50-lucio

Cambio: recompensa `base`, `--log_std_init -0.5` (desvío inicial 0.61), seed 1

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 7: control de exploración](../../docs/pruebas-recompensas-2026-10-15.md#tanda-7-control--base-con-menos-ruido-de-exploración-sin-tocar-la-recompensa) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `base` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (67 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 5% / 40% / 74%. Cruza 50 %: 0.97M.
- **Best** (1.3M), 100 episodios: 70% (IC 60–78 %). {'tiempo': 3, 'choque_plataforma': 25, 'exito': 70, 'choque_inclinacion': 1, 'choque_piso': 1}.
  Δacción 0.20, Δv pedida 0.139 m/s.
- **Final** (1.5M), 100 episodios: 79% (IC 70–86 %). {'exito': 79, 'choque_plataforma': 19, 'tiempo': 1, 'choque_inclinacion': 1}.
  Δacción 0.46, Δv pedida 0.216 m/s.

**Lectura:** Control: base con desvío inicial 0.61 aprende con la seed 1.
