# v17-lucio

Cambio: misma configuración que v16, entrenada 5M pasos en vez de 200k

| | v16-lucio | v17-lucio |
|---|---|---|
| Éxito best (100 ep.) | 4% (2–10) | **85% (77–91)** |
| Best éxito (8 ep.) | 0% | 100% |
| Best reward | −9.16 | 20.63 |
| Largo ep. (best) | 103 pasos | 56 pasos |
| Best en timestep | 200 000 | 3 700 000 |
| Timesteps totales | 200 704 | 5 001 216 (2.2 h, 8 entornos) |

## Qué cambió
- Solo la cantidad de pasos: 200k → 5M. Mismo código de entrenamiento (los commits entre las dos corridas
  son el README, el arreglo de los flags bool y el registro de v16), mismos hiperparámetros, mismo entorno
  y misma seed (42).

## Por qué
Ver `runs/v16-lucio/NOTES.md`: con 200k pasos el dron se tiraba al piso, y había que ver si con más
entrenamiento salía de esa trampa, como pasó en las corridas viejas (0 % hasta 1–2.2M pasos y después ~95 %).

## Resultado
**Datos.**
- **Aprendió, y antes que las corridas viejas:** el éxito en las evaluaciones de 8 episodios pasó de 0 % a
  25 % a los 0.4M pasos, tuvo un primer 100 % a los 0.7M y desde ~2.3M se mantiene entre 62.5 % y 100 %.
  Las viejas despegaban entre 1M y 2.2M. Durante el entrenamiento, al final, 98 % de éxito.
- **Evaluación de 100 episodios del best (3.7M):** 85 % de éxito (IC 95 %: 77–91 %). El 100 % de las
  evaluaciones de 8 episodios era optimista.
- **Los fallos son choques contra el borde de la plataforma:** 14 de los 15. En todos, el dron está a
  0.24–0.32 m del centro (el radio es 0.25 m). Llega a la plataforma pero golpea el canto. El otro es un
  choque por inclinación. Ninguno contra el piso (en v16 eran 80 de 100).
- **Aterriza rápido:** mediana de 2.5 s (p90: 3.3 s) de los 20 disponibles.
- **Normalización:** ningún valor se recorta en más del 1 % de los pasos. La velocidad angular en x e y
  queda justo debajo (0.8 % y 0.7 %; p99.9 ~8.9 rad/s contra una escala de 5).
- El crítico funciona sin escalar la recompensa (`explained_variance` ~0.85 al final). La política sigue
  explorando bastante (`std` 1.39).

**Hipótesis.**
- El incentivo a chocar contra el piso existió al principio (hasta 0.3M), pero no impidió aprender.
- Que aprenda antes que las viejas probablemente se debe al límite de velocidad más alto (0.6 m/s, ahora
  puede alcanzar la plataforma) o a la normalización fija. No se puede separar, porque cambiaron juntas, y
  además las viejas usaban otra configuración.
- Los choques contra el borde pueden venir de que aterriza muy rápido y cerca del canto. El criterio de
  contacto nuevo (base contra tope) cuenta esos golpes como choque; con el viejo, algunos contaban como
  `top`.

## Próximo paso
1. Repetir con las seeds 1 y 2 (misma configuración) para saber si este resultado es de la configuración
   o de la suerte de la seed 42. Es la base contra la cual comparar todo lo demás.
2. Atacar los choques contra el borde: por ejemplo, premiar estar cerca del centro al tocar, o castigar la
   velocidad horizontal relativa al aterrizar. Comparar con la evaluación de 100 episodios.
3. Subir `OBS_ANG_VEL_SCALE` a ~10 rad/s (p99.9 ~8.9).
