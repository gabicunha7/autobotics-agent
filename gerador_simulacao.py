import csv
import random
from datetime import datetime, timedelta
import json

ARQUIVO = "dados_simulados.csv"


NUM_SERIAIS = [f"{i:04d}" for i in range(1, 16)]


SETOR_POR_SERIAL = {
    "0001": "Fabricacao de Componentes",
    "0002": "Fabricacao de Componentes",
    "0003": "Fabricacao de Componentes",

    "0004": "Desenvolvimento de Tecnologias",
    "0005": "Desenvolvimento de Tecnologias",
    "0006": "Desenvolvimento de Tecnologias",
    "0007": "Desenvolvimento de Tecnologias",

    "0008": "Estamparia",
    "0009": "Estamparia",
    "0010": "Estamparia",
    "0011": "Estamparia",

    "0012": "Montagem final",
    "0013": "Montagem final",
    "0014": "Montagem final",
    "0015": "Montagem final",
}

NOME_PROCESSOS = [
"modbus",
"PROFINET",
"robot_controller",
"inverse_kinematics",
"path_follower",
"gripper_control",
"lidar_scan",
"camera_stream",
"force_sensor",
"user_input",
"task_scheduler",
]

disco_usado_atual = {serial: random.uniform(20, 40) for serial in NUM_SERIAIS}


dias_passados = 0


def atualizar_disco(serial, dias_passados):
    """Atualiza lentamente o uso de disco com comportamento realista."""

    valor = disco_usado_atual[serial]


    valor += random.uniform(0.3, 0.5)

    if dias_passados % 14 == 0 and dias_passados != 0:
        valor += random.uniform(5.0, 10.5)

    if valor > 95:
        valor -= random.uniform(50.5, 70.0)

    valor = max(5.0, min(95.0, valor))

    disco_usado_atual[serial] = valor
    return round(valor, 2)



with open(ARQUIVO, "w", newline="") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow([
        "timestamp", "empresa", "setor", "numSerial", "cpu", "ramTotal", "ramUsada", "discoTotal", "discoUsado", 
        "numProcessos", "top5Processos"
    ])

ano_atual = datetime.now().year

inicio_geral = datetime(ano_atual, 1, 1, 0, 0)
fim_geral = datetime(ano_atual, 12, 1, 23, 0)

inicio_dia2 = datetime(ano_atual, 12, 2, 0, 0)
fim_dia2 = datetime(ano_atual, 12, 2, 23, 59)


def gerar_top5():
    lista = []
    for i in range(5):
        lista.append({
            "pid": random.randint(100, 9999),
            "name": random.choice(NOME_PROCESSOS),
            "cpu_percent": round(random.uniform(0, 40), 2),
            "memory_rss": round(random.uniform(0, 40), 2),
        })
    return lista


with open(ARQUIVO, "a", newline="") as f:
    writer = csv.writer(f, delimiter=";")

    tempo = inicio_geral
    incremento_horas = timedelta(hours=1)

    dias_passados = 0
    ultimo_dia = tempo.day

    while tempo <= fim_geral:

  
        if tempo.day != ultimo_dia:
            dias_passados += 1
            ultimo_dia = tempo.day

        for serial in NUM_SERIAIS:

            setor = SETOR_POR_SERIAL[serial]  
            cpu = round(random.uniform(1, 95), 2)
            ram_total = 16.00
            ram_usada = round(random.uniform(20, 95), 2)
            disco_total = 512.00
            empresa = "Porsche"

  
            disco_usado = atualizar_disco(serial, dias_passados)

            num_processos = random.randint(50, 300)
            top5 = gerar_top5()

            writer.writerow([
                tempo.strftime("%Y-%m-%d %H:%M:%S"),
                empresa,
                setor,
                serial,
                cpu,
                ram_total,
                ram_usada,
                disco_total,
                disco_usado,
                num_processos,
                json.loads(json.dumps(top5))
            ])

        tempo += incremento_horas

    tempo = inicio_dia2
    incremento_minutos = timedelta(minutes=5)

    while tempo <= fim_dia2:

        for serial in NUM_SERIAIS:

            setor = SETOR_POR_SERIAL[serial] 
            cpu = round(random.uniform(1, 95), 2)
            ram_total = 16.00
            ram_usada = round(random.uniform(20, 95), 2)
            disco_total = 512.00
            empresa = "Porsche"

            disco_usado = atualizar_disco(serial, dias_passados)

            num_processos = random.randint(50, 300)
            top5 = gerar_top5()

            writer.writerow([
                tempo.strftime("%Y-%m-%d %H:%M:%S"),
                empresa,
                setor,
                serial,
                cpu,
                ram_total,
                ram_usada,
                disco_total,
                disco_usado,
                num_processos,
                json.loads(json.dumps(top5))
            ])

        tempo += incremento_minutos

print("Arquivo CSV gerado com sucesso:", ARQUIVO)
