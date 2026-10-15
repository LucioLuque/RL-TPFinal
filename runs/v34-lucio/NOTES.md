# v34-lucio

Cambio: progreso k=3 además de la distancia (`A2_k3`), seed 2

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 5: tres seeds](../../docs/pruebas-recompensas-2026-10-15.md#tanda-5-tres-seeds-de-base-a2_k3-y-suave_c002) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `A2_k3` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (68 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 15% / 72% / 80%. Cruza 50 %: 0.62M.
- **Best** (1.4M), 100 episodios: 81% (IC 72–88 %). {'exito': 81, 'choque_plataforma': 18, 'choque_piso': 1}.
  Δacción 0.71, Δv pedida 0.248 m/s.
- **Final** (1.5M), 100 episodios: 80% (IC 71–87 %). {'exito': 80, 'choque_piso': 2, 'choque_plataforma': 17, 'tiempo': 1}.
  Δacción 0.77, Δv pedida 0.253 m/s.

**Lectura:** A2_k3 seed 2: la mejor de A2_k3.
