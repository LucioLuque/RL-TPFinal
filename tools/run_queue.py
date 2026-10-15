"""Corre una cola de entrenamientos en paralelo y evalua cada corrida al terminar (best y final, 100 episodios).

    python -m tools.run_queue cola.txt --parallel 2

Cada linea de la cola: `<run_id> <recompensa> <seed> <timesteps> [args extra de train.py]`, por ejemplo
`v68-lucio suave_bajada 42 1500000 --log_std_init -0.5`. Lineas vacias o con # se ignoran. Se saltean las
corridas que ya tienen runs/<run_id>/ (asi se puede cortar y volver a lanzar). La cola se relee en cada vuelta:
se pueden agregar lineas mientras corre. Logs en logs/queue/<run_id>*.log.

Memoria: cada corrida usa ~3.5 GB (8 entornos de entrenamiento + 8 de evaluacion). En una maquina de 13-16 GB,
no pasar de 2 en paralelo (con 3 se lleno la RAM el 2026-10-15). Cada corrida de 1.5M tarda ~55 min con 3 en
paralelo en 8 nucleos.

Para correrlo sin que muera al cerrar la terminal: `setsid nohup python -m tools.run_queue cola.txt > logs/queue.log 2>&1 &`
"""
import argparse
import os
import subprocess
import sys
import time

from utils import get_run_dir

LOG_DIR = os.path.join("logs", "queue")


def read_queue(path: str) -> list[list[str]]:
    with open(path) as f:
        return [line.split() for line in f if line.strip() and not line.lstrip().startswith("#")]


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

        pending = [j for j in read_queue(args.queue)
                   if j[0] not in launched and not os.path.exists(get_run_dir(j[0]))]
        if pending and len(running) < args.parallel:
            rid, reward, seed, timesteps, *extra = pending[0]
            print(f"{time.strftime('%H:%M')} lanzo {rid}: {reward} seed {seed} {timesteps} {' '.join(extra)}", flush=True)
            running[rid] = subprocess.Popen(job_command(rid, reward, seed, timesteps, extra), shell=True, env=env)
            launched.add(rid)
            time.sleep(30)  # que cree runs/<rid>/ antes de mirar la cola de nuevo
            continue
        if not pending and not running:
            print("Cola terminada.", flush=True)
            return
        time.sleep(20)


if __name__ == "__main__":
    main()
