# Entrenar en las máquinas del laboratorio S004 (UdeSA) por SSH

Resumen de la wiki del laboratorio, <https://it-ing-udesa.github.io/>, leída el 2026-10-29. El laboratorio
está en fase experimental y la wiki puede cambiar: ante una duda o algo que no funcione, ir a la fuente.
La segunda parte dice cómo usarlo para este proyecto, con lo aprendido al usarlo la noche del 2026-10-29 (actualizada
el 2026-10-31).

## Lo que dice la wiki

### Máquinas

22 máquinas compartidas entre materias de Ingeniería. Cada una tiene: Intel Core i7-14700K, NVIDIA RTX 4090,
32 GB de RAM, NVMe de 1 TB (Linux) y Ubuntu 24.04.5.

### Quién puede entrar

Quienes cursan Principios de la Robótica Autónoma, Visión Artificial, Procesamiento del Lenguaje Natural,
Bioinformática o Taller de Proyecto Final, y quienes hacen la tesis de grado. Los demás piden acceso con el
[formulario](https://forms.gle/iLZS8ugCkU3pDpR18). Se entra con el usuario y la contraseña del mail `@udesa.edu.ar`.
La primera vez que uno se loguea puede tardar más de lo normal.

### Horario del acceso remoto

| Días | Horario |
|---|---|
| Lunes a viernes | 22:00 a 07:00 |
| Sábados, domingos y feriados | Todo el día |

- De lunes a viernes, a las **06:50** aparece un aviso y a las **07:00** se cortan las sesiones SSH. Lo que corre
  dentro de `tmux` sigue vivo hasta las **07:30**, cuando **se reinician todas las máquinas y se pierde cualquier
  proceso**.
- Si entre las 07:00 y las 22:00 de un día hábil la contraseña se acepta pero la conexión se cierra enseguida
  (`Connection closed by ... port 22`), es porque el acceso está fuera de horario. Con una contraseña incorrecta,
  en cambio, aparece `Permission denied, please try again`. Si pasa un feriado, puede que ese día no esté cargado
  como feriado.
- Hay mantenimiento programado el primer día de cada mes, de noche.
- La ocupación presencial del aula está en el calendario de la portada de la wiki.

### VPN (hace falta antes del SSH)

- **openfortivpn** (Linux, versión ≥ 1.23):
  ```bash
  sudo openfortivpn gateway.udesa.edu.ar:443 -u <usuario> --saml-login   # abre el navegador para loguearse
  ```
- **FortiClient VPN 7.4** (Linux y Windows), descargado de <https://www.fortinet.com/lat/support/product-downloads>.
  En ☰ al lado de *VPN Name* → *Add a new connection*: VPN `SSL-VPN`, nombre `UdeSA VPN`, Remote Gateway
  `gateway.udesa.edu.ar:443` y `gateway-2.udesa.edu.ar:443`, marcar *Enable Single Sign On (SSO) for VPN Tunnel*,
  Client Certificate `None`. Guardar, elegir `UdeSA VPN` y hacer click en *SAML Login*.

La wiki solo nombra esos dos clientes. No dice nada de macOS, pero openfortivpn anda con Homebrew: ver
[Conectarse desde macOS](#conectarse-desde-macos-una-vez).

### SSH

```bash
ssh <usuario>@labs004.udesa.edu.ar          # con la VPN conectada
ssh -XYC <usuario>@labs004.udesa.edu.ar     # con interfaz gráfica (X11; solo desde clientes Linux)
```

- La conexión asigna una máquina, y cada conexión siguiente te manda **a la misma**, así que lo que quedó en su
  disco local se puede volver a usar.
- **Hasta 2 conexiones simultáneas por usuario.** Cada `ssh`, `scp`, `sftp` o `rsync` cuenta como una. Con dos
  sesiones abiertas, hay que cerrar una antes de copiar archivos. Para tener varias terminales, usar `tmux`
  dentro de una sola conexión.
- Copiar archivos, desde una terminal de **tu computadora** (no desde la sesión SSH):
  ```bash
  scp -r carpeta/ <usuario>@labs004.udesa.edu.ar:~/scratch/      # subir
  scp -r <usuario>@labs004.udesa.edu.ar:~/scratch/work/x .       # bajar
  ```
- Si aparece `REMOTE HOST IDENTIFICATION HAS CHANGED`, la máquina asignada se reinstaló: correr
  `ssh-keygen -R labs004.udesa.edu.ar` y volver a conectarse. Si no se había anunciado ninguna reinstalación,
  avisar a soporte.

### Almacenamiento

| Directorio | Dónde está | Límite | Persistencia | Lo ven las otras máquinas |
|---|---|---|---|---|
| `$HOME` (`/home/<usuario>`) | NFS | **2 GB y 25 000 archivos** | Persistente | Sí |
| `~/scratch` (`/scratch/<usuario>`) | Disco local de la máquina | El espacio libre del disco | **Se borra al final de cada cuatrimestre** y al reinstalar | No |
| `~/Downloads` (`~/scratch/downloads`) | Disco local | El de `~/scratch` | Igual que `~/scratch` | No |

- En el home va lo liviano: código, configuración. Entornos, datasets, cachés y checkpoints van en `~/scratch`.
  `quota` muestra cuánto se está usando. Si se pasa el límite, no se pueden guardar archivos nuevos.
- Antes de que termine el cuatrimestre, mover al home lo que se quiera conservar de `~/scratch`.

### Software

- Instalado: `tmux`, `nvtop` y `btop` (para ver el uso de GPU, CPU y RAM), `git`, `rsync`, `curl`, `wget`,
  `python3-venv`, `python3-dev`, `uv`, CUDA toolkit, `build-essential` y `cmake`.
- **No hay permisos de administrador** (no se puede usar `apt`). Los paquetes de Python se instalan en un entorno
  virtual. Las herramientas de PyPI, con `uv tool install`. Los binarios, en `~/scratch`.
- La wiki recomienda `uv` y crear los entornos en `~/scratch/work/` (pueden ocupar varios GB). Las cachés de `uv` ya
  están configuradas para ir a `~/scratch`. `uv pip install torch` trae las librerías de CUDA. Con
  `uv init`/`uv sync`, definir `UV_PROJECT_ENVIRONMENT` para que el `.venv` no quede en el home.
- Para pedir software nuevo, escribir a soporte, con dos semanas de anticipación al inicio del cuatrimestre.

### Reglas de uso

- Uso académico solamente. **No ocupar toda la CPU o toda la GPU por mucho tiempo, ni dejar procesos corriendo sin
  supervisión.** Antes de lanzar algo, mirar con `btop` o `nvtop` cuánto se está usando la máquina.
- Los trabajos que tengan que sobrevivir al reinicio de las 07:30 quedan fuera de lo que cubre el laboratorio.
- No compartir las credenciales. Al terminar, cerrar la sesión.
- Soporte: **soporte-s004@udesa.edu.ar** (lunes a viernes de 9 a 18; responden en unos 2 días hábiles). Las fallas de
  hardware van a ticketsti@udesa.edu.ar. En el mail, poner el usuario, la máquina (`hostname`, por ejemplo
  `labo-s004-05`), la materia o el proyecto y una descripción del problema.

## Cómo usarlo para este proyecto

### Conectarse desde macOS (una vez)

Probado el 2026-10-29 desde la Mac de Teo. La wiki no cubre macOS, pero openfortivpn anda igual que en Linux.

```bash
brew install openfortivpn
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_labs004 -N ""   # clave sin contraseña: así Claude puede conectarse solo
```

Agregar a `~/.ssh/config`:

```
Host labs004
  HostName labs004.udesa.edu.ar
  User tkaucher                 # el usuario del mail @udesa.edu.ar
  IdentityFile ~/.ssh/id_ed25519_labs004
  IdentitiesOnly yes
  ControlMaster auto
  ControlPath ~/.ssh/cm-%r@%h:%p
  ControlPersist 4h
  ServerAliveInterval 60
```

Con la VPN levantada (ver abajo), copiar la clave al laboratorio. Pide la contraseña del mail una sola vez:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_labs004.pub labs004
ssh -o BatchMode=yes labs004 hostname    # tiene que responder sin pedir contraseña (por ejemplo, labo-s004-16)
```

- **La clave y `~/.ssh/config` los tiene que crear uno a mano:** los permisos de Claude Code no lo dejan escribir en
  `~/.ssh`.
- `ControlMaster` hace que todos los `ssh` y `rsync` compartan una sola conexión. Así nunca se pasa el límite de 2
  conexiones simultáneas. Pero si esa conexión se traba, se traban todos los comandos: ver
  [Dejar a Claude entrenando solo](#dejar-a-claude-entrenando-solo).

### Levantar la VPN (cada vez)

En una terminal de la Mac:

```bash
sudo -v && { (sleep 2 && open "https://gateway.udesa.edu.ar:443/remote/saml/start?redirect=1") & sudo openfortivpn gateway.udesa.edu.ar:443 -u tkaucher --saml-login; }
```

1. Pide la contraseña de la Mac (la de `sudo`).
2. A los 2 segundos se abre el navegador con el login de la universidad. Hay que loguearse en **menos de ~50 s**:
   openfortivpn deja de esperar y hay que empezar de nuevo. Sin el `open`, el navegador no se abre solo.
3. Cuando la terminal dice `Tunnel is up and running`, la VPN está arriba. **Esa terminal tiene que quedar abierta.**

- **Claude no puede levantar la VPN:** hace falta la contraseña de `sudo` y el login en el navegador.
- **La VPN dura ~8 horas.** La noche del 2026-10-29 se levantó a las ~23:05 y se cayó sola a las ~07:00 (a la mañana
  openfortivpn ya no estaba corriendo). Probablemente es el límite de sesión de FortiGate, que por defecto es de 8 h;
  no está confirmado. Hay que anotar a qué hora se levantó: ~8 h después, Claude ya no puede traer nada.
- Para saber si está arriba: `nc -z -G 5 labs004.udesa.edu.ar 22` (si responde `succeeded`, hay VPN).

### Instalación en el laboratorio (una vez por cuatrimestre, o cuando se borre `~/scratch`)

El repo pesa ~250 MB y tiene ~1100 archivos (con `.git`), así que entra en el home (2 GB y 25 000 archivos) y ahí no
se borra. El entorno va en `~/scratch`. No hay conda: se usa `uv`, con Python 3.12, que es el que pide
gym-pybullet-drones.

```bash
cd ~ && git clone https://github.com/LucioLuque/RL-TPFinal.git && cd RL-TPFinal
git config user.name Teo           # Lucio, el suyo. El autor de v<N>-<autor> es la primera palabra de user.name,
                                   # en minúsculas (utils.get_author): "Teo" -> teo, pero "teomk" daría teomk.
                                   # Sin user.name queda 'unknown'.

uv venv --python 3.12 ~/scratch/work/venvs/rl-tpfinal
source ~/scratch/work/venvs/rl-tpfinal/bin/activate
uv pip install -r requirements.txt   # con GPU NVIDIA: no hace falta el torch solo CPU del README
```

- **Los comandos remotos van con `bash -lc`** (`ssh labs004 'bash -lc "..."'`). Un `ssh labs004 '<comando>'` suelto no
  carga `/etc/profile.d`, que es donde se manda la caché de `uv` a `~/scratch`. El 2026-10-29, instalar así llenó la
  cuota del home con la caché de torch (en `~/.cache/uv`), y hubo que borrarla.
- Para hacer `git push` desde el laboratorio hace falta autenticarse con GitHub (un token o una clave SSH en `~/.ssh`
  del laboratorio). No está configurado.

### Entrenar

`labs004` manda siempre a la misma máquina (hasta ahora, `labo-s004-16`), así que lo que quedó en su `~/scratch` se
puede reusar. Ahí hay dos scripts, en `~/scratch/work/`. Si se borra `~/scratch`, se crean de nuevo con este
contenido:

```bash
# cola.sh: corre la cola (dentro de tmux)
#!/bin/bash -l
source ~/scratch/work/venvs/rl-tpfinal/bin/activate
cd ~/RL-TPFinal
mkdir -p logs
python -m tools.run_queue cola_pendiente.txt --parallel 3 2>&1 | tee -a logs/queue.log
```

```bash
# corte.sh: a las 06:40 desactiva las líneas que no se lanzaron, que no llegarían a terminar antes del reinicio de las 07:30
#!/bin/bash
while [ "$(date +%H%M)" -lt 0640 ] || [ "$(date +%H%M)" -gt 1200 ]; do sleep 60; done
sed -i -E "s/^([a-z_0-9]+ [0-9]+ [0-9]+.*)$/# no lanzada (corte de las 06:40): \1/" ~/RL-TPFinal/cola_pendiente.txt
echo "$(date +%H:%M) corte: lineas pendientes desactivadas" >> ~/RL-TPFinal/logs/queue.log
```

Para lanzar (desde la Mac, con la VPN arriba):

```bash
ssh labs004 'bash -lc "cd ~/RL-TPFinal && git status --short && git pull"'
ssh labs004 'uptime; free -g'      # que la máquina no esté ocupada por otro (a mano: ssh -t labs004 btop, salir con q)
ssh labs004 'tmux new -d -s rl ~/scratch/work/cola.sh && tmux new-window -d -t rl -n corte ~/scratch/work/corte.sh'
```

Para entrenar con cambios que todavía no están commiteados, copiarlos antes de lanzar, como se hizo el 2026-10-29:
`rsync -a env.py train.py caps.py rewards.yaml cola_pendiente.txt tools labs004:RL-TPFinal/`. Cada corrida guarda ese
estado en su `diff.patch`. Después, el `git pull` del laboratorio puede chocar con esos archivos: mirar el
`git status` y, si ya están commiteados, descartar la copia (`git checkout -- <archivo>`) antes del pull.

Para mirar la cola en vivo: `ssh -t labs004 tmux attach -t rl`, y para salir sin cortar nada, `Ctrl+B` y después `D`.
Lo que hizo cada corrida queda en `~/RL-TPFinal/logs/queue.log` y en `~/RL-TPFinal/logs/queue/<id>.log`.

- **Tiempos medidos** (2026-10-30, 3 corridas en paralelo): **3M pasos tardan 31–41 min por corrida**, del
  lanzamiento al final, contando las dos evaluaciones de 100 episodios. Entre las 00:29 y las 06:41 entraron 31
  corridas de 3M.
- **Todo muere a las 07:30 de los días hábiles.** `train.py` guarda `model.zip` recién al final (`best/` se va guardando
  cada 100k pasos, cuando mejora), así que **una corrida cortada pierde el modelo final**. Por eso `corte.sh`.
- **RAM:** cada corrida usa ~3.5 GB. Con 3 en paralelo, la máquina usaba 22 de 31 GB. La máquina es compartida y la
  regla es no ocuparla entera: 3 como mucho, si está libre. El entrenamiento usa sobre todo CPU (16
  procesos de PyBullet por corrida), no la GPU.
- La interfaz gráfica de `eval.py` solo anda con `ssh -XYC` desde Linux. Para evaluar en el laboratorio, usar
  `tools.evaluate` (sin GUI), y los gifs o la GUI hacerlos en la computadora propia.

### Dejar a Claude entrenando solo

**Qué falló la noche del 2026-10-29.** Las 31 corridas terminaron bien, pero Claude solo trajo y registró hasta v119.
Las 16 siguientes (v120–v135) recién se pudieron traer la noche del 31, porque:

1. **Los avisos se trabaron sin decir nada.** Claude esperaba con `until ssh labs004 'ls <archivos>'; do sleep 60; done`
   en segundo plano, para despertarse cuando aparecieran. Desde las ~03:24, ningún `ssh` vio nada, aunque las
   corridas terminaron entre las 03:45 y las 06:41 y el puerto del laboratorio respondía. La causa más probable es que
   se trabó la conexión compartida (`ControlMaster`): los `ssh` que pasan por ella esperan para siempre, y
   `ConnectTimeout` no los corta, porque no abren una conexión nueva. Además, los errores iban a `/dev/null`, así que
   no quedó registro de qué pasó.
2. **No había plan B.** Claude solo se despertaba si se cumplía la condición. Como nunca se cumplió, no volvió a mirar
   nada hasta que la persona volvió.
3. **A las 07:00 se cortó todo:** el SSH del laboratorio, como cada día hábil, y la VPN, ~8 h después de levantarla.
   Pasadas las 07:00, lo que no se trajo espera hasta las 22:00 o hasta el fin de semana. No se perdió nada, porque
   `runs/` está en el home del laboratorio, que no se borra.

**Reglas:**
- **Todo `ssh` o `rsync` automático tiene un tope de tiempo** y, si falla, se cierra la conexión compartida para que el
  próximo abra una nueva. Los errores se ven: nada de `2>/dev/null`.
- **Esperar siempre con un tope:** el aviso sale cuando termina una corrida **o** a los 30 min, lo que pase primero.
  Nunca esperar una condición que podría no cumplirse.
- **Traer cada corrida apenas termina** (`rsync` copia solo lo nuevo) y registrarla, en vez de dejar todo para el final.
- **Planear la noche con las dos horas límite:** la caída de la VPN (~8 h después de levantarla) y el corte del SSH
  (07:00 los días hábiles). Lo que termine después queda en el laboratorio y se trae la noche siguiente. Si la VPN se
  cae, Claude no la puede levantar: tiene que esperar a la persona.
- Antes de suponer que una corrida falló, mirar `logs/queue.log` en el laboratorio: dice cuáles terminaron y con qué
  código.

**Funciones** (probadas el 2026-10-31 en la Mac, desde la raíz del repo). macOS no trae `timeout`; `perl -e 'alarm'`
corta el comando a los N segundos (sale con código 142):

```bash
con_tope() { perl -e 'alarm shift; exec @ARGV' "$@"; }
cortar() { con_tope 10 ssh -O exit labs004 2>/dev/null || pkill -f 'labs004.*\[mux\]'; }   # cierra la conexión compartida
lab() {    # ssh al laboratorio con un tope de 60 s
  con_tope 60 ssh -o BatchMode=yes -o ConnectTimeout=20 labs004 "$@" && return 0
  local codigo=$?; echo "$(date +%H:%M) falló ssh (código $codigo): cierro la conexión compartida" >&2; cortar; return $codigo
}
traer() {  # trae runs/ y los logs de la cola; -u no pisa lo que esté más nuevo acá (por ejemplo, las NOTES.md)
  con_tope 600 rsync -au -e 'ssh -o BatchMode=yes' labs004:RL-TPFinal/runs/ runs/ &&
  con_tope 120 rsync -au -e 'ssh -o BatchMode=yes' labs004:RL-TPFinal/logs/queue/ logs/queue/ ||
  { echo "$(date +%H:%M) falló rsync: cierro la conexión compartida" >&2; cortar; return 1; }
}
```

**Espera** (Claude la corre en segundo plano y se despierta cuando termina; tarda como mucho ~1 h):

```bash
# Sale cuando termina una corrida nueva o a los 30 min, lo que pase primero; antes de salir, trae lo nuevo.
antes=$(lab 'grep -c termino ~/RL-TPFinal/logs/queue.log')
for i in $(seq 15); do
  sleep 120
  ahora=$(lab 'grep -c termino ~/RL-TPFinal/logs/queue.log') || continue
  [ "$ahora" != "$antes" ] && break
done
traer
date +%H:%M; lab 'grep -v pybullet ~/RL-TPFinal/logs/queue.log | tail -5'
```

Cada vez que se despierta: registrar lo que trajo (`/registrar-corrida`), decidir si cambia algo de la cola y volver
a lanzar la espera. Traer todo la primera vez tarda ~20 s, y después solo copia lo nuevo.

### Traer los resultados

Desde la raíz del repo en la Mac, con la VPN arriba: `traer` (ver arriba), o a mano:

```bash
rsync -au labs004:RL-TPFinal/runs/ runs/ && rsync -au labs004:RL-TPFinal/logs/queue/ logs/queue/
```

Después, `/registrar-corrida` como siempre. Commitear y hacer push desde el laboratorio también serviría, pero no
está configurado (falta autenticarse con GitHub), y los commits se aprueban antes de hacerlos.
