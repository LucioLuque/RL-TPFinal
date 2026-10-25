"""Corre una cola de entrenamientos en paralelo y evalua cada corrida al terminar (best y final, 100 episodios).

    python -m tools.run_queue cola.txt --parallel 2

Cada linea de la cola: `<recompensa> <seed> <timesteps> [args extra de train.py]`, por ejemplo
`suave_bajada 42 1500000 --log_std_init -0.5`. Lineas vacias o con # se ignoran. El numero de la corrida no va en la
cola: se asigna al lanzarla (el siguiente libre, como train.py sin --run_id), asi no quedan numeros reservados ni
huecos. Al lanzar una linea, se la marca en el archivo como `# lanzada como v105-lucio (HH:MM): <linea>`, para que no se
relance y quede a la vista que numero le toco. La cola se relee en cada vuelta: se pueden agregar o sacar lineas
mientras corre. Logs en logs/queue/<run_id>*.log.

Las colas viejas, con el run_id al principio de cada linea (`v68-lucio suave_c002 2 1500000 ...`), siguen
funcionando: esas lineas se saltean si ya existe runs/<run_id>/.

Memoria: cada corrida usa ~3.5 GB (8 entornos de entrenamiento + 8 de evaluacion). En una maquina de 13-16 GB,
no pasar de 2 en paralelo (con 3 se lleno la RAM el 2026-10-15). Cada corrida de 1.5M tarda ~50 min con 2 en
paralelo en 8 nucleos.

Para correrlo sin que muera al cerrar la terminal: `setsid nohup python -m tools.run_queue cola.txt > logs/queue.log 2>&1 &`
"""
import argparse
import os
import subprocess
import sys
import time

from utils import RUN_TAG_RE, get_next_run_id, get_run_dir

LOG_DIR = os.path.join("logs", "queue")
LAUNCHED_PREFIX = "# lanzada como"


def read_queue(path: str) -> list[tuple[int, list[str]]]:
    """(indice de linea, palabras) de cada linea pendiente."""
    with open(path) as f:
        lines = f.read().splitlines()
    return [(i, line.split()) for i, line in enumerate(lines) if line.strip() and not line.lstrip().startswith("#")]


def mark_launched(path: str, index: int, rid: str) -> None:
    """Comenta la linea lanzada, con el numero que le toco."""
    with open(path) as f:
        lines = f.read().splitlines()
    lines[index] = f"{LAUNCHED_PREFIX} {rid} ({time.strftime('%H:%M')}): {lines[index].strip()}"
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def new_run_id() -> str:
    """Siguiente numero libre. Crea runs/<id>/ en el momento, para que el proximo lanzamiento no saque el mismo."""
    rid = get_next_run_id()
    os.makedirs(get_run_dir(rid))
    return rid


def job_command(rid: str, reward: str, seed: str, timesteps: str, extra: list[str]) -> str:
    py = sys.executable
    log = os.path.join(LOG_DIR, rid)
    return (
        f"{py} train.py --run_id {rid} --reward {reward} --seed {seed} --timesteps {timesteps} {' '.join(extra)} "
        f"> {log}.log 2>&1 "
        f"&& ({py} -m tools.evaluate --load {rid} --best > {log}_eval_best.log 2>&1; "
        f"{py} -m tools.evaluate --load {rid} > {log}_eval_final.log 2>&1)"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("queue", help="Archivo con la cola.")
    parser.add_argument("--parallel", type=int, default=2, help="Corridas a la vez (default 2, ver memoria).")
    args = parser.parse_args()

    os.makedirs(LOG_DIR, exist_ok=True)
    # OMP/MKL en 1 hilo: con varias corridas a la vez, torch con varios hilos compite por los nucleos.
    env = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    running: dict[str, subprocess.Popen] = {}
    launched: set[str] = set()

    while True:
        for rid, proc in list(running.items()):
            if proc.poll() is not None:
                print(f"{time.strftime('%H:%M')} termino {rid} (codigo {proc.returncode})", flush=True)
                del running[rid]

        # Las lineas con run_id explicito (formato viejo) se saltean si esa corrida ya existe.
        pending = [(i, words) for i, words in read_queue(args.queue)
                   if not (RUN_TAG_RE.match(words[0]) and (words[0] in launched or os.path.exists(get_run_dir(words[0]))))]
        if pending and len(running) < args.parallel:
            index, words = pending[0]
            if RUN_TAG_RE.match(words[0]):
                rid, (reward, seed, timesteps, *extra) = words[0], words[1:]
            else:
                rid, (reward, seed, timesteps, *extra) = new_run_id(), words
                mark_launched(args.queue, index, rid)
            print(f"{time.strftime('%H:%M')} lanzo {rid}: {reward} seed {seed} {timesteps} {' '.join(extra)}", flush=True)
            running[rid] = subprocess.Popen(job_command(rid, reward, seed, timesteps, extra), shell=True, env=env)
            launched.add(rid)
            time.sleep(30)  # que train.py arranque antes de lanzar la siguiente
            continue
        if not pending and not running:
            print("Cola terminada.", flush=True)
            return
        time.sleep(20)


if __name__ == "__main__":
    main()
