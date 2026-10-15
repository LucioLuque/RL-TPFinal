# v36-lucio

Cambio: castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 2

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 5: tres seeds](../../docs/pruebas-recompensas-2026-10-15.md#tanda-5-tres-seeds-de-base-a2_k3-y-suave_c002) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `suave_c002` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (75 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 26% / 56% / 73%. Cruza 50 %: 0.66M.
- **Best** (1.4M), 100 episodios: 74% (IC 65–82 %). {'exito': 74, 'choque_piso': 3, 'choque_plataforma': 20, 'tiempo': 3}.
  Δacción 0.09, Δv pedida 0.075 m/s.
- **Final** (1.5M), 100 episodios: 75% (IC 66–82 %). {'exito': 75, 'choque_plataforma': 21, 'choque_piso': 2, 'tiempo': 2}.
  Δacción 0.10, Δv pedida 0.076 m/s.

**Lectura:** suave_c002 seed 2.
