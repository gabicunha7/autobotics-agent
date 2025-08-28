import getpass
import time
from datetime import datetime
import psutil
import pandas as pd

# Inicializa o dicionário de dados
dados = {
    "user": [],
    "timestamp": [],
    "cpu percent total": [],
}

# Detecta o número de núcleos e prepara colunas para cada núcleo
num_nucleos = psutil.cpu_count(logical=True)
for i in range(num_nucleos):
    nome_coluna = f"cpu percent core {i + 1}" # "+1" pra contagem não começar do zero
    dados[nome_coluna] = []

# Adicionando colunas de RAM
dados["ram total GB"] = []
dados["ram usada GB"] = []
dados["ram percent"] = []

# Adicionando colunas de Disco
dados["disk total GB"] = []
dados["disk usado GB"] = []
dados["disk percent"] = []

# Criando laço de repetição
rodando = True

while rodando:
    # Usuário e timestamp
    dados["user"].append(getpass.getuser())
    dados["timestamp"].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # CPU total
    dados["cpu percent total"].append(psutil.cpu_percent(interval=1, percpu=False))

    # CPU por núcleo
    cpu_por_nucleo = psutil.cpu_percent(interval=None, percpu=True)
    for i in range(num_nucleos):
        nome_coluna = f"cpu percent core {i + 1}"
        dados[nome_coluna].append(cpu_por_nucleo[i])

    # RAM
    mem = psutil.virtual_memory()
    dados["ram total GB"].append(round(mem.total / (1024**3), 2))
    dados["ram usada GB"].append(round(mem.used / (1024**3), 2))
    dados["ram percent"].append(mem.percent)

    # Disco (C:)
    disco = psutil.disk_usage('C:\\')
    dados["disk total GB"].append(round(disco.total / (1024**3), 2))
    dados["disk usado GB"].append(round(disco.used / (1024**3), 2))
    dados["disk percent"].append(disco.percent)

    # Salva em CSV
    df = pd.DataFrame(dados)
    df.to_csv("dados-sistema.csv", sep=";", index=False, encoding="utf-8")

    # Espera 5 segundos
    time.sleep(5)