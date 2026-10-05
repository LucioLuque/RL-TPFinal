# v22-lucio

Cambio: recompensa XY: distancia horizontal pesada 3 veces más que la altura

Se compara contra v21 (`base` con el PID arreglado, misma seed 42 y 1.5M pasos).

| | v21-lucio (`base`) | v22-lucio (`XY`) |
|---|---|---|
| `rollout/success_rate` a 0.75M / 1.0M / 1.5M | 31% / 62% / 72% | 0% / 0% / 4% |
| Primer paso con ≥ 50% (entrenamiento) | 0.86M | nunca (≤ 1.5M) |
| Éxito best (100 ep.) | 65% (55–74), best a 0.9M | 35% (26–45), best a 1.5M |
| Choques contra la plataforma (100 ep.) | 31 | 10 |
| Terminan por tiempo (100 ep.) | 1 | 48 |
| Tiempo hasta aterrizar (mediana) | 2.4 s | 10.5 s |
| Largo ep. a 1.5M (entrenamiento) | 78 pasos | 385 pasos |
| Timesteps totales | 1 503 232 | 1 503 232 (35 min) |

## Qué cambió
Variante de recompensa `XY` (`--reward XY`): `−0.1·d_xy − 0.033·|dz|` en vez de `−0.1·d`. El resto igual a
v21 (commit `2ff0a3b`, sin cambios sin commitear): hiperparámetros, entorno, seed (42) y PID arreglado. Los
coeficientes se eligieron para que el castigo total por paso quede parecido al de `base`.

## Por qué
En v17 y v21, casi todos los fallos son choques contra el borde bajando en diagonal desde afuera de la
plataforma: con `−0.1·d`, bajar achica el castigo igual que acercarse en horizontal. Con `XY`, alinearse
arriba vale 3 veces más que bajar (`BITACORA.md`, 2026-10-04).

## Resultado
**Datos.**
- **Se alinea, pero no baja.** En los 48 episodios que terminan por tiempo, el dron está **encima** de la
  plataforma (a 0.10 m del centro) pero flotando a ~20 cm sobre el tope, hasta que se acaba el tiempo.
- **Los choques contra el borde bajaron** (10 contra 31), pero casi todo eso se fue a episodios por tiempo,
  no a aterrizajes. Los 10 que quedan tienen el mismo patrón de antes (afuera y bajo).
- **Aprende mucho más lento:** 0 % de éxito en el entrenamiento hasta 1.25M; recién al final empieza a
  aterrizar (4 % en el entrenamiento y 37.5 % en la evaluación de 8 episodios a 1.5M). El best es el último
  checkpoint, así que todavía estaba mejorando.
- Cuando aterriza, tarda mucho: mediana de 10.5 s (`base`: 2.4 s).

**Hipótesis.** Con el castigo por altura bajo (0.033), quedarse arriba de la plataforma cuesta casi nada, y
bajar arriesga un choque. Es el mismo fenómeno que en A1 (v18): cuando la recompensa deja de empujar a
terminar el episodio, el agente prefiere flotar. Logró alinearse, que era lo buscado, pero le faltó
el empuje para bajar.

## Próximo paso
- Pendiente decidir cómo atacar los choques contra el borde. Una opción es `XY` con más castigo por altura
  (por ejemplo, 0.1 y 0.066) o entrenada más tiempo, porque al final de la corrida estaba empezando a
  aterrizar.
