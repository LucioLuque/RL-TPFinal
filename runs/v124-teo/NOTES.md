# v124-teo

Cambio: acción como velocidad (`action_mode: velocity`, `suave_bajada_c003_vel`), 3M, seed 42

| | v105-teo | v124-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 97% (92–99) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 20.61 | 21.37 |
| Largo ep. (best) | 58.0 | 53.1 |
| Best en timestep | 3,000,000 | 2,100,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 100 |
| Final: centro, mediana / < 5 cm | 4.1 cm / 60% | 3.7 cm / 71% |
| Final: llega a tocar a (mediana, m/s) | 0.51 | 0.51 |
| Final: Δacción / Δv pedida (p95) | 0.034 / 0.063 (0.154) m/s | 0.058 / 0.068 (0.163) m/s |
| Final: inclinación RMS / jerk (m/s³) | 6.9° / 31 | 7.0° / 31 |

## Qué cambió
- **Acción** (`env.py`, `action_mode: velocity`, opción nueva apagada por defecto): la velocidad pedida es
  `0.6·(dx, dy, dz)` (si la norma pasa de 1, se escala a 1) en vez de `0.6·s·dir/|dir|`. `s` no se usa: el entorno lo
  pone en 0, y así entra en la observación y en el castigo a la acción. Para frenar alcanza con achicar la acción;
  antes había que bajar `s`, que está saturado en 1.
- `tools/evaluate.py` calcula la velocidad pedida con `_commanded_velocity` del entorno, así que mide bien en los dos
  modos. **`Δacción` incluye la salida `s` de la red, que en este modo no se usa y cambia libremente: comparar con
  `Δv pedida`.**
- Variante `suave_bajada_c003_vel` en `rewards.yaml`: `suave_bajada_c003` + `action_mode: velocity`.
- Mismo resto que v105-teo (seed 42, desvío 0.61, 3M). Laboratorio S004, 3 corridas en paralelo.

## Por qué
`s` está en 1 en el 100 % de los pasos de todas las políticas (`tools/action_saturation.py`): el dron vuela siempre a
0.6 m/s y no puede frenar al tocar. Por eso ni castigar (`_flare`) ni premiar (`_tocar`, v111–v113) la velocidad de
toque funcionó. Esta corrida es el control (sin premio por tocar despacio) de `suave_bajada_c003_vel_tocar` (v127).

## Resultado
- 100 %, y **aprende antes**: 50 % a 0.51M (v105: 0.67M) y 5 de 8 en el eval de 0.5M.
- Centra parecido (3.7 cm, 71 % a menos de 5 cm; v105: 4.1 cm, 60 %), con una suavidad parecida (Δv pedida 0.068
  contra 0.063 m/s).
- **Sigue tocando a 0.51 m/s:** `dz` está saturado en el 78 % de los pasos (v107: 75 %). Poder frenar no alcanza si
  nada en la recompensa lo pide.

## Próximo paso
- Ver v126 (3 seeds) y v127–v129, con premio por tocar despacio.
