# v35-lucio

Cambio: castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 1

Parte de las pruebas de recompensa del 2026-10-15: ver [Tanda 5: tres seeds](../../docs/pruebas-recompensas-2026-10-15.md#tanda-5-tres-seeds-de-base-a2_k3-y-suave_c002) en
`docs/pruebas-recompensas-2026-10-15.md`, donde se compara con las demás corridas.

- **Recompensa:** `suave_c002` (coeficientes en `run.json`, `env_kwargs`). Hiperparámetros como v21, salvo lo indicado.
- **Timesteps:** 1,503,232 (73 min, en paralelo con otras corridas).
- **Éxito en el entrenamiento** (`rollout/success_rate`, estocástica) a 0.5M / 1M / 1.5M: 20% / 61% / 74%. Cruza 50 %: 0.66M.
- **Best** (1.2M), 100 episodios: 72% (IC 62–80 %). {'choque_plataforma': 24, 'choque_piso': 1, 'exito': 72, 'tiempo': 2, 'choque_inclinacion': 1}.
  Δacción 0.15, Δv pedida 0.087 m/s.
- **Final** (1.5M), 100 episodios: 76% (IC 67–83 %). {'choque_plataforma': 20, 'choque_piso': 3, 'exito': 76, 'tiempo': 1}.
  Δacción 0.30, Δv pedida 0.144 m/s.

**Lectura:** suave_c002 seed 1 aprende (base con esa seed no).
