---
name: registrar-corrida
description: Registra una corrida de entrenamiento de RL-TPFinal. Lee runs/<run_id>/run.json, la compara con la corrida anterior (código, reward, obs, hiperparámetros, entorno y resultados), escribe runs/<run_id>/NOTES.md y regenera EXPERIMENTS.md. Usar después de cada entrenamiento, o cuando el usuario pida registrar o documentar una corrida.
argument-hint: "[run_id] [vs run_id_anterior]"
---

# Registrar corrida

Objetivo: que cada corrida quede documentada con qué cambió respecto de la anterior, por qué, qué
resultado dio y qué probar después. Los números ya los guarda `train.py` en `runs/<run_id>/run.json`;
este registro agrega la interpretación.

## 1. Elegir las corridas

- **Corrida a registrar**: la de `$ARGUMENTS` si se indicó (`v16-lucio`, o `15` para las viejas que
  son `version_15`). Si no, la de `runs/*/run.json` con el `started_at` más reciente que todavía no
  tenga `NOTES.md`. Si hay más de una sin registrar, avisar y registrarlas de la más vieja a la más nueva.
- **Corrida de comparación**: la indicada con `vs <run_id>` si se pasó. Si no, la corrida anterior
  en número que tenga `run.json`. Si la corrida a registrar continúa una anterior (`--load`), cada
  sesión nueva se compara con la sesión previa de la misma corrida.
  Si la de comparación es de otro autor, decirlo en la nota.
- Si la corrida tiene `status` `running`, avisar que todavía no terminó (o que se cortó sin escribir
  el estado, por ejemplo si se mató el proceso) y preguntar si registrarla igual.

## 2. Reconstruir qué cambió

El código con el que se entrenó cada corrida es su `git.commit` + su `diff.patch`. Comparar:

- **Reward y observación**: `diff runs/<anterior>/env.py runs/<actual>/env.py` (copias exactas).
  Mirar `_computeReward`, `_computeObs` y las condiciones de aterrizaje/choque. Ver `obs_dim`.
- **Entorno/nivel**: `level`, `env_kwargs` y `env_constants` (límite de velocidad del dron y escalas de
  normalización de la observación) en ambos `run.json`, y `diff` de los `levels.yaml`. Las corridas
  anteriores a la normalización fija no tienen `env_constants`: usaban `VecNormalize`.
- **Hiperparámetros y args**: `hyperparams` y `args` de ambos `run.json`.
- **Resto del código** (`train.py`, `utils.py`, etc.): `git diff <commit_anterior> <commit_actual>`
  sobre esos archivos, teniendo en cuenta los `diff.patch` de cada una. Ignorar `runs/`, `logs/` y `media/`.
- **Motivo**: buscarlo en `BITACORA.md` (entradas que mencionen la corrida o que sean posteriores a la
  corrida anterior), en los mensajes de commit entre ambas corridas
  (`git log <commit_anterior>..<commit_actual>`) y en esta conversación. Si no aparece, preguntarle
  al usuario en una sola pregunta por qué hizo el cambio. Si no lo sabe, escribir "Motivo: no registrado".

Si un mensaje de commit dice algo que el código no hace (por ejemplo, anuncia un término de reward
que está comentado), señalarlo en la nota.

## 3. Leer los resultados

De `results` en `run.json`:

- `best_success_rate`, `best_mean_reward`, `best_mean_ep_length` y `best_at_timesteps`.
- `evals`, para ver la tendencia: si sigue subiendo al final (conviene entrenar más), si se estancó o si colapsó.

Tener en cuenta que la tasa de éxito sale de `n_eval_episodes` episodios (8 por defecto), así que
va de a 12.5%. Una diferencia de un episodio no es señal: decirlo así y no sacar conclusiones fuertes.

**Evaluación de 100 episodios (el número que vale para comparar).** Si la corrida no tiene
`runs/<run_id>/eval_best.json`, correr desde la raíz del repo, con el entorno `drone-landing`:

```bash
conda run -n drone-landing python -m tools.evaluate --load <run_id> --best --episodes 100
```

Usa siempre las mismas semillas, así que todas las corridas se evalúan sobre los mismos episodios. De
`eval_best.json` usar: `success_rate` y `success_ci95` (intervalo del 95 %), `outcomes` (cómo terminan:
`exito`, `choque_piso`, `choque_plataforma`, `choque_inclinacion`, `tiempo`), `landing_time_s` y
`obs_clipped_fraction` (si algún valor se recorta en más del 1 % de los pasos, sugerir subir su escala).
Si los intervalos de dos corridas se superponen mucho, no afirmar que una es mejor que la otra.

## 4. Escribir `runs/<run_id>/NOTES.md`

En español, corto y concreto. Con este formato (la línea `Cambio:` la usa `tools/experiments_index.py` para el índice, así que va en una sola línea, de no más de ~80 caracteres):

```markdown
# <run_id>

Cambio: <el cambio principal en una línea>

| | <anterior> | <actual> |
|---|---|---|
| Éxito best (100 ep.) | 78% (69–85) | 85% (77–91) |
| Best éxito (8 ep.) | 40% | 62% |
| Best reward | ... | ... |
| Largo ep. (best) | ... | ... |
| Best en timestep | ... | ... |
| Timesteps totales | ... | ... |

## Qué cambió
- <cada cambio de reward, obs, entorno, hiperparámetros o código, con los valores antes → después>

## Por qué
<motivo, o "no registrado">

## Resultado
<qué pasó, con la tendencia de los evals; separar lo que muestran los datos de lo que es hipótesis>

## Próximo paso
<1-2 cosas concretas para probar>
```

## 5. Regenerar el índice

Correr `python -m tools.experiments_index` desde la raíz del repo. Si `python` no está en el PATH, usar `python3`; el script no necesita las dependencias del proyecto. No editar `EXPERIMENTS.md` a mano.

Al final, mostrarle al usuario la línea `Cambio:` y la tabla de la nota. No commitear salvo que lo pida.
