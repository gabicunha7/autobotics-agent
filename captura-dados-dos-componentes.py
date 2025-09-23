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
        writer.writerow(["nomeMaquina", "nomeUsuario", "nomeDoSO", "RealeaseDoSO", "VersãoDoSO", "Processador", "NúcleosFísicos", "NúcleosLógicos"])
except FileExistsError:
    pass

# Cria arquivo com cabeçalho dos dados do hardware
try:
    with open(ARQUIVO2, "x", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerow(["timestamp", "nomeMaquina", "nomeUsuario", "cpu", "ramTotal", "ramUsada", "discoTotal", "discoUsado"])
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

# Cria a função para enviar mensagem no canal de suporte usando o InfoMan
# def enviar_mensagem_slack(menssagem):
#     textoEnviado = {'text': menssagem}
#     requests.post(SLACK_WEBHOOK_URL, json=textoEnviado)

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
        
        print(f"{timestamp} | Nome da Máquina: {nomeMaquina} | Nome de usuário: {nomeUsuario} | CPU: {uso}% | Ram total: {ramTotal}GB | Ram em Uso: {ramUsada}% | Disco total: {discoTotal}GB | Disco em uso: {discoUsado}%")
        
        # if uso > 95:
        #     enviar_mensagem_slack(f":warning: ALERTA NA MÁQUINA: {nomeMaquina} Uso de CPU acima de 50%! Atual: {uso}%")
        #     print("\n Notificação enviada no Slack - #alertas \n")
        # elif ramUsada > 90:
        #     enviar_mensagem_slack(f":warning: ALERTA NA MÁQUINA: {nomeMaquina} Uso de RAM acima de 70%! Atual: {ramUsada}%")
        #     print("\n Notificação enviada no Slack - #alertas \n")
        # elif discoUsado > 97:
        #     enviar_mensagem_slack(f":warning: ALERTA NA MÁQUINA: {nomeMaquina} Uso de disco acima de 97%! Atual: {discoUsado}%")
        #     print("\n Notificação enviada no Slack - #alertas \n")
        
        with open(ARQUIVO2, "a", newline="") as f:
            writer = csv.writer(f, delimiter="|")
            writer.writerow([timestamp, nomeMaquina, nomeUsuario, uso, ramTotal, ramUsada, discoTotal, discoUsado])
        
        time.sleep(10)

except KeyboardInterrupt:  # (Ctrl + c)
    print("\n=== Captura finalizada ===")
