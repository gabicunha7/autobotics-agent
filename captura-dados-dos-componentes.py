import psutil
import getpass
import platform
import time
import csv
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv(override=True)

print("Diretório atual:", os.getcwd())

print("Variáveis do banco:")
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASSWORD:", os.getenv("DB_PASSWORD"))
print("DB_DATABASE:", os.getenv("DB_DATABASE"))

ARQUIVO = "dados_gerais.csv"
ARQUIVO2 = "dados_hardware.csv"

# Cria arquivo com cabeçalho dos dados gerais do servidor (só na primeira vez)
try:
    with open(ARQUIVO, "x", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["nomeMaquina", "nomeUsuario", "nomeDoSO", "RealeaseDoSO", "VersaoDoSO", "Processador", "NucleosFisicos", "NucleosLogicos"])
except FileExistsError:
    pass

# Cria arquivo com cabeçalho dos dados do hardware (só na primeira vez)
try:
    with open(ARQUIVO2, "x", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "timestamp", "nomeMaquina", "nomeUsuario", "cpu", "ramTotal", "ramUsada",
            "discoTotal", "discoUsado", "numProcessos", "top5Processos"
        ])
except FileExistsError:
    pass

# Informações do SO e máquina
nomeSo = platform.system()
realeaseSo = platform.release()
versaoSO = platform.version()
processador = platform.processor()
nucleosFisicos = psutil.cpu_count(logical=False)
nucleosLogicos = psutil.cpu_count(logical=True)
nomeMaquina = platform.node()
nomeUsuario = getpass.getuser()

with open(ARQUIVO, "a", newline="") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow([nomeMaquina, nomeUsuario, nomeSo, realeaseSo, versaoSO, processador, nucleosFisicos, nucleosLogicos])

print("\n=== Iniciando Captura Contínua ===\n")

# config = {
#     'host': os.getenv("DB_HOST"),
#     'user': os.getenv("DB_USER"),
#     'password': os.getenv("DB_PASSWORD"),
#     'database': os.getenv("DB_DATABASE"),
# }

config = {
     'host': 'localhost',
     'user': 'agente',
     'password': 'sptech',
     'database': 'autobotics',
 }

try:
   
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("Conexão bem-sucedida ao banco de dados!")


    cursor.execute("SELECT * FROM parametro")
    results = cursor.fetchall()
    if results:
        print("SELECT executado com sucesso. Resultados encontrados:")
        for row in results:
            print(row)
    else:
        print("SELECT executado com sucesso, mas não retornou resultados.")

    while True:
        uso = psutil.cpu_percent(interval=1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ramTotal = round(psutil.virtual_memory().total / (1024**3), 2)
        ramUsada = psutil.virtual_memory().percent
        discoTotal = round(psutil.disk_usage("/").total / (1024**3), 2)
        discoUsado = psutil.disk_usage("/").percent
        numProcessos = len(psutil.pids())

        processos = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processos.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        top5 = sorted(processos, key=lambda x: x['cpu_percent'], reverse=True)[:5]
        top5Processos = ",".join([f"{p['name']}({p['pid']}):{p['cpu_percent']}%" for p in top5])

        print(f"{timestamp} | Máquina: {nomeMaquina} | Usuário: {nomeUsuario} | "
              f"CPU: {uso}% | RAM: {ramUsada}% de {ramTotal}GB | "
              f"Disco: {discoUsado}% de {discoTotal}GB | "
              f"Processos: {numProcessos} | Top5: {top5Processos}")

        # Grava no CSV
        with open(ARQUIVO2, "a", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([
                timestamp, nomeMaquina, nomeUsuario, uso, ramTotal, ramUsada,
                discoTotal, discoUsado, numProcessos, top5Processos
            ])

        query_insert = """
            INSERT INTO dados_hardware (
                timestamp, nome_maquina, nome_usuario, cpu_percent,
                ram_total_gb, ram_usada_percent, disco_total_gb, disco_usado_percent,
                num_processos, top5_processos
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            timestamp, nomeMaquina, nomeUsuario, uso,
            ramTotal, ramUsada, discoTotal, discoUsado,
            numProcessos, top5Processos
        )

        cursor.execute(query_insert, valores)
        conn.commit()
        print("Dados inseridos no banco com sucesso.")

        time.sleep(10)  

except mysql.connector.Error as err:
    print(f"Erro no banco de dados: {err}")

except KeyboardInterrupt:
    print("\n=== Captura finalizada pelo usuário ===")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("Conexão com o banco encerrada.")
