# v24-lucio

Cambio: castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 42

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 1 (seed 42)](../../docs/pruebas-recompensas-2026-10-15.md#tanda-1-seed-42) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `suave_c002` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (77 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 14% / 57% / 75%. Cruza 50 %: 0.63M.
- **Best** (1.4M), 100 episodios: 67% (IC 57–75 %). {'tiempo': 5, 'exito': 67, 'choque_piso': 2, 'choque_plataforma': 26}.
  Δacción 0.20, Δv pedida 0.119 m/s.
- **Final** (1.5M), 100 episodios: 72% (IC 62–80 %). {'choque_plataforma': 21, 'exito': 72, 'choque_piso': 3, 'tiempo': 4}.
  Δacción 0.26, Δv pedida 0.133 m/s.

**Lectura:** Mismo éxito que base, aprende antes y cambia la acción ~3 veces menos.
