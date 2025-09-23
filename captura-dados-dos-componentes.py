import psutil
import getpass
import platform
import time
import csv
# import requests
from datetime import datetime

ARQUIVO = "dados_gerais.csv"
ARQUIVO2 = "dados_hardware.csv"

# Cria arquivo com cabeçalho dos dados gerais do servidor (só na primeira vez)
try:
    with open(ARQUIVO, "x", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerow(["nomeMaquina", "nomeUsuario", "nomeDoSO", "RealeaseDoSO", "VersaoDoSO", "Processador", "NucleosFisicos", "NucleosLogicos"])
except FileExistsError:
    pass

# Cria arquivo com cabeçalho dos dados do hardware
try:
    with open(ARQUIVO2, "x", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerow([
            "timestamp", "nomeMaquina", "nomeUsuario", "cpu", "ramTotal", "ramUsada",
            "discoTotal", "discoUsado", "numProcessos", "top5Processos"
        ])
except FileExistsError:
    pass

# Informações do SO
nomeSo = platform.system()
realeaseSo = platform.release()
versaoSO = platform.version()
processador = platform.processor()
nucleosFisicos = psutil.cpu_count(logical=False)
nucleosLogicos = psutil.cpu_count(logical=True)
nomeMaquina = platform.node()
nomeUsuario = getpass.getuser()

with open(ARQUIVO, "a", newline="") as f:
    writer = csv.writer(f, delimiter="|")
    writer.writerow([nomeMaquina, nomeUsuario, nomeSo, realeaseSo, versaoSO, processador, nucleosFisicos, nucleosLogicos])

print("\n")
print("\n=== Iniciando Captura Contínua ===")

try:
    while True:
        uso = psutil.cpu_percent(interval=1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ramTotal = round(psutil.virtual_memory().total / (1024**3), 2)
        ramUsada = psutil.virtual_memory().percent
        discoTotal = round(psutil.disk_usage("/").total / (1024**3), 2)
        discoUsado = psutil.disk_usage("/").percent

        # Número de processos
        numProcessos = len(psutil.pids())

        # Top 5 processos que mais estão usando CPU
        processos = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processos.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        top5 = sorted(processos, key=lambda x: x['cpu_percent'], reverse=True)[:5]
        top5Processos = "; ".join([f"{p['name']}({p['pid']}):{p['cpu_percent']}%" for p in top5])

        # Print no terminal
        print(f"{timestamp} | Máquina: {nomeMaquina} | Usuário: {nomeUsuario} | "
              f"CPU: {uso}% | RAM: {ramUsada}% de {ramTotal}GB | "
              f"Disco: {discoUsado}% de {discoTotal}GB | "
              f"Processos: {numProcessos} | Top5: {top5Processos}")

        # Grava no CSV
        with open(ARQUIVO2, "a", newline="") as f:
            writer = csv.writer(f, delimiter="|")
            writer.writerow([
                timestamp, nomeMaquina, nomeUsuario, uso, ramTotal, ramUsada,
                discoTotal, discoUsado, numProcessos, top5Processos
            ])

        time.sleep(10)

except KeyboardInterrupt:  # (Ctrl + c)
    print("\n=== Captura finalizada ===")
