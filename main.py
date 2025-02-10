import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import time

# Função para conectar ao banco de dados
def conectar():
    return psycopg2.connect(
        host="localhost",        
        dbname="BD_SENSORES",     
        user="caio",      
        password="2246",    
        port="5432"
    )

# Função para registrar logs
def registrar_log(mensagem, status):
    try:
        with open("sync_log.txt", "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{timestamp} - {status} - {mensagem}\n")
    except Exception as e:
        print(f"Erro ao escrever no log: {e}")

# Função para buscar sensores do banco
def carregar_sensores():
    connection = conectar()
    cursor = connection.cursor()
    
    cursor.execute("SELECT id, nome FROM sensores;")
    sensores = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return {str(s[0]): s[1] for s in sensores}  # Retorna {id: nome}

# Função para inserir leitura
def inserir_leitura():
    sensor_id = sensor_combobox.get().split(" - ")[0]  # Pega o ID
    valor = valor_entry.get()

    if not sensor_id or not valor:
        messagebox.showwarning("Atenção", "Preencha todos os campos!")
        return

    try:
        valor = float(valor)
        timestamp = datetime.now()

        connection = conectar()
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO leitura_sensores (sensor_id, valor, timestamp, sincronizado)
            VALUES (%s, %s, %s, FALSE)
        """, (sensor_id, valor, timestamp))
        
        connection.commit()
        cursor.close()
        connection.close()

        messagebox.showinfo("Sucesso", "Leitura inserida com sucesso!")
        valor_entry.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao inserir leitura: {e}")

# Função para adicionar um novo sensor
def adicionar_sensor():
    nome = nome_entry.get()
    tipo = tipo_entry.get()
    unidade = unidade_entry.get()
    localizacao = localizacao_entry.get()

    if not nome or not tipo or not unidade or not localizacao:
        messagebox.showwarning("Atenção", "Preencha todos os campos!")
        return

    try:
        connection = conectar()
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO sensores (nome, tipo, unidade, localizacao, ativo)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (nome, tipo, unidade, localizacao))
        
        connection.commit()
        cursor.close()
        connection.close()

        messagebox.showinfo("Sucesso", "Sensor adicionado com sucesso!")

        # Atualizar a lista de sensores no Combobox
        sensores = carregar_sensores()
        sensor_combobox["values"] = [f"{k} - {v}" for k, v in sensores.items()]

        # Limpar os campos de entrada
        nome_entry.delete(0, tk.END)
        tipo_entry.delete(0, tk.END)
        unidade_entry.delete(0, tk.END)
        localizacao_entry.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao adicionar sensor: {e}")

# Função para buscar a última leitura de um sensor específico
def buscar_ultima_leitura():
    sensor_id = consulta_sensor_combobox.get().split(" - ")[0]  # Pega o ID

    if not sensor_id:
        messagebox.showwarning("Atenção", "Selecione um sensor!")
        return

    try:
        connection = conectar()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT s.nome, s.tipo, l.valor, s.unidade, l.timestamp 
            FROM leitura_sensores l
            JOIN sensores s ON l.sensor_id = s.id
            WHERE l.sensor_id = %s AND l.sincronizado = TRUE
            ORDER BY l.timestamp DESC
            LIMIT 1;
        """, (sensor_id,))

        leitura = cursor.fetchone()
        cursor.close()
        connection.close()

        if leitura:
            nome, tipo, valor, unidade, horario = leitura
            resultado_text.set(f"🔹 Nome: {nome}\n🔹 Tipo: {tipo}\n🔹 Última Leitura: {valor} {unidade}\n🔹 Horário: {horario}")
        else:
            resultado_text.set("Nenhuma leitura sincronizada encontrada para este sensor.")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao buscar leitura: {e}")

# Função para registrar logs e salvar no banco
def registrar_log(status_bool, mensagem):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Grava no arquivo de log
    with open("sync_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} | {'Sucesso' if status_bool else 'Erro'} | {mensagem}\n")

    # Grava na tabela `sincronizacao`
    try:
        connection = conectar()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO sincronizacao (timestamp, status, mensagem) VALUES (%s, %s, %s)",
            (timestamp, status_bool, mensagem)  # status agora é booleano
        )
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Erro ao registrar sincronização no banco: {e}")

# Função para sincronizar dados
def sincronizar():
    while True:
        try:
            connection = conectar()
            cursor = connection.cursor()

            # Buscar leituras não sincronizadas
            cursor.execute("SELECT id FROM leitura_sensores WHERE sincronizado = FALSE;")
            leituras = cursor.fetchall()

            if not leituras:
                registrar_log(True, "Nenhum dado para sincronizar.")
            else:
                # Marcar como sincronizados
                cursor.execute("UPDATE leitura_sensores SET sincronizado = TRUE WHERE sincronizado = FALSE;")
                connection.commit()

                registrar_log(True, f"Successful Connection: {len(leituras)} leituras sincronizadas.")

            cursor.close()
            connection.close()

        except Exception as e:
            registrar_log(False, f"Connection Failure: {e}.")

        # Aguardar 60 segundos antes da próxima execução
        for _ in range(60):
            if parar_thread:
                return
            time.sleep(1)

# Criando uma thread para rodar a sincronização em segundo plano
parar_thread = False
thread = threading.Thread(target=sincronizar, daemon=True)
thread.start()

# Janela principal
root = tk.Tk()
root.title("Gerenciamento de Sensores")
root.geometry("550x400")  
root.resizable(False, False)

# Abas
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Aba inserir leitura
frame_leitura = ttk.Frame(notebook)
notebook.add(frame_leitura, text="Inserir Leitura")

ttk.Label(frame_leitura, text="Selecione o Sensor:").pack(pady=5)
sensores = carregar_sensores()
sensor_combobox = ttk.Combobox(frame_leitura, values=[f"{k} - {v}" for k, v in sensores.items()], state="readonly")
sensor_combobox.pack(pady=5)

ttk.Label(frame_leitura, text="Valor da Leitura:").pack(pady=5)
valor_entry = ttk.Entry(frame_leitura)
valor_entry.pack(pady=5)

ttk.Button(frame_leitura, text="Salvar Leitura", command=inserir_leitura).pack(pady=10)

# Aba consultas
frame_consulta = ttk.Frame(notebook)
notebook.add(frame_consulta, text="Consultar Leituras")

ttk.Label(frame_consulta, text="Selecione o Sensor:").pack(pady=5)
consulta_sensor_combobox = ttk.Combobox(frame_consulta, values=[f"{k} - {v}" for k, v in sensores.items()], state="readonly")
consulta_sensor_combobox.pack(pady=5)

ttk.Button(frame_consulta, text="Buscar Última Leitura", command=buscar_ultima_leitura).pack(pady=10)

resultado_text = tk.StringVar()
ttk.Label(frame_consulta, textvariable=resultado_text, justify="left", padding=10).pack(pady=10)


# Aba adicionar sensor
frame_sensor = ttk.Frame(notebook)
notebook.add(frame_sensor, text="Adicionar Sensor")

ttk.Label(frame_sensor, text="Nome do Sensor:").pack(pady=5)
nome_entry = ttk.Entry(frame_sensor)
nome_entry.pack(pady=5)

ttk.Label(frame_sensor, text="Tipo:").pack(pady=5)
tipo_entry = ttk.Entry(frame_sensor)
tipo_entry.pack(pady=5)

ttk.Label(frame_sensor, text="Unidade de Medida:").pack(pady=5)
unidade_entry = ttk.Entry(frame_sensor)
unidade_entry.pack(pady=5)

ttk.Label(frame_sensor, text="Localização:").pack(pady=5)
localizacao_entry = ttk.Entry(frame_sensor)
localizacao_entry.pack(pady=5)

ttk.Button(frame_sensor, text="Adicionar Sensor", command=adicionar_sensor).pack(pady=10)

# Botão sair
ttk.Button(root, text="Sair", command=root.quit).pack(pady=10)

# Iniciar interface gráfica
root.mainloop()
