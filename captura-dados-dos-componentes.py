import psutil
import platform
import time
import csv
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os
import boto3
import json
import getpass

load_dotenv()

ARQUIVO = "dados_gerais.csv"
ARQUIVO2 = "dados_hardware.csv"
numSerial = "0001"

try:
    with open(ARQUIVO, "x", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["nomeMaquina", "nomeUsuario", "nomeDoSO", "RealeaseDoSO", "VersaoDoSO", "Processador", "NucleosFisicos", "NucleosLogicos", "NumeroSerial"])
except FileExistsError:
    pass

def cria_comeco_hw():
    try:
        with open(ARQUIVO2, "x", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([
                "timestamp", "numSerial", "cpu", "ramTotal", "ramUsada",
                "discoTotal", "discoUsado", "numProcessos", "top5Processos"
            ])
    except FileExistsError:
        pass

cria_comeco_hw()

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
    writer.writerow([nomeMaquina, nomeUsuario, nomeSo, realeaseSo, versaoSO, processador, nucleosFisicos, nucleosLogicos, numSerial])

print("\n=== Iniciando Captura Contínua ===\n")

config = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_DATABASE"),
}

try:
   
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("Conexão bem-sucedida ao banco de dados!")


    cursor.execute("SELECT * FROM parametro")
    results = cursor.fetchall()
    if results:
        print("SELECT na tabela 'parametro' executado com sucesso. Resultados encontrados:")

    else:
        print("SELECT executado com sucesso, mas não retornou resultados.")

    while True:
        uso = psutil.cpu_percent(interval=1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ramTotal = psutil.virtual_memory().total
        ramUsada = psutil.virtual_memory().percent
        discoTotal = psutil.disk_usage("/").total
        discoUsado = psutil.disk_usage("/").percent
        numProcessos = len(psutil.pids())
        nomeMaquina = platform.node()
        nomeUsuario = getpass.getuser()

        processos = []
        ram_total = psutil.virtual_memory().total

        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                rss_bytes = p.info['memory_info'].rss
        
               # RAM em percentual
                mem_percent = round((rss_bytes / ram_total) * 100, 2)

               # CPU normalizado
                cpu_raw = p.cpu_percent(interval=0.1)
                cpu_percent_real = round(cpu_raw / psutil.cpu_count(), 2)

                processos.append({
                    "pid": p.pid,
                    "name": p.info['name'],
                    "cpu_percent": cpu_percent_real,
                    "memory_percent": mem_percent
                })

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        top5 = sorted(processos, key=lambda x: x['cpu_percent'], reverse=True)[:5]
        top5_json = json.dumps(top5, indent=2)


        print(f"{timestamp} | Máquina: {nomeMaquina} | Usuário: {nomeUsuario} | "
              f"CPU: {uso}% | RAM: {ramUsada}% de {ramTotal}B | "
              f"Disco: {discoUsado}% de {discoTotal}B | "
              f"Processos: {numProcessos} | Top5: {json.loads(top5_json)}")

        with open(ARQUIVO2, "a", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([
                 timestamp, numSerial, uso, ramTotal, ramUsada,
                discoTotal, discoUsado, numProcessos, json.loads(top5_json)
            ])

        cursor.execute("SELECT id_controlador FROM controlador WHERE numero_serial = %s", (numSerial,))
        id_controlador = cursor.fetchone()[0]

        query_insert = """
            update telemetria 
            set timestamp = %s,
                nome_maquina = %s,
                nome_usuario = %s,
                cpu_percent = %s,
                ram_total_gb = %s,
                ram_usada_percent = %s,
                disco_total_gb = %s,
                disco_usado_percent = %s,
                num_processos = %s,
                top5_processos = %s
            WHERE fk_controlador = %s
        """

        valores = (
            timestamp, nomeMaquina, nomeUsuario, uso,
            round(ramTotal / (1024 ** 3), 2), ramUsada, round(discoTotal / (1024 ** 3),2), discoUsado,
            numProcessos, top5_json, id_controlador
        )

        cursor.execute(query_insert, valores)
        conn.commit()
        print("Dados inseridos no banco com sucesso.")

        time.sleep(10)  

        if datetime.now().second < 10:
            try:
                s3 = boto3.client('s3')
                nome_bucket = 'raw-1d4a3f130793f4b0dfc576791dd86b32'
                
                caminho = f"{numSerial}-{(timestamp.replace(':', '-')).replace(' ', '-')}.csv"
                s3.upload_file(ARQUIVO2, nome_bucket, caminho)
                print("Dados CSV enviado para o bucket com sucesso!")
                os.remove(ARQUIVO2)
                cria_comeco_hw()

            except Exception as e:
                print(f"Erro em enviar csv")

except mysql.connector.Error as err:
    print(f"Erro no banco de dados: {err}")

except KeyboardInterrupt:
    print("\n=== Captura finalizada pelo usuário ===")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("Conexão com o banco encerrada.")




