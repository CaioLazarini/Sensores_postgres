# 📡 Gerenciamento de Sensores com Interface Gráfica e Sincronização Automática

Este projeto é uma **aplicação Python** para gerenciar sensores e suas leituras, utilizando uma **interface gráfica (Tkinter)** e **sincronização automática com PostgreSQL**.  

## 🚀 Funcionalidades

✔️ **Interface gráfica (Tkinter)** para adicionar e gerenciar sensores  
✔️ **Registro de leituras de sensores** com data/hora  
✔️ **Sincronização automática** de leituras a cada 1 minuto  
✔️ **Registro de logs de sincronização** em um arquivo (`sync_log.txt`)  
✔️ **Consulta de leituras sincronizadas** por sensor  

## 🛠️ Tecnologias Utilizadas

- **Python 3**
- **PostgreSQL** (Banco de Dados)
- **Tkinter** (Interface Gráfica)
- **Psycopg2** (Conexão com o banco)
- **Threading** (Execução paralela da sincronização)

## 📥 Instalação

1. **Clone o repositório**:
   
   git clone https://github.com/CaioLazarini/Sensores_postgres.git

2.Instale as dependências:

  pip install psycopg2 tk

3.Configure o banco de dados (PostgreSQL):

4.Inicie o banco de dados disponibilizado na pasta "File_db" ou 
execute os seguintes comandos para criar as tabelas:

CREATE TABLE sensores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(255) NOT NULL,
    unidade VARCHAR(20) NOT NULL,
    localizacao VARCHAR(255) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE leitura_sensores (
    id SERIAL PRIMARY KEY,
    sensor_id INT NOT NULL,
    valor DECIMAL(6, 2) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    sincronizado BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_sensor FOREIGN KEY (sensor_id) REFERENCES sensores(id) ON DELETE CASCADE
);

CREATE TABLE sincronizacao (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    status BOOLEAN NOT NULL,
    mensagem VARCHAR(255) DEFAULT NULL
);


▶️ Como Usar

Execute o programa:

python main.py

Funcionalidades da Interface:

📌 Aba "Inserir Leitura" → Adicione leituras para um sensor existente.
🔎 Aba "Consultar Leituras" → Consulte a última leitura sincronizada de um sensor.
➕ Aba "Adicionar Sensor" → Registre novos sensores no sistema.
A sincronização automática ocorre a cada 1 minuto, registrando no banco e no log sync_log.txt.

Para sair, clique no botão "Sair" ou feche a janela.

📄 Estrutura do Código

gerenciamento-sensores/
│── main.py           # Código principal (interface + sincronização)
│── sync_log.txt      # Registro de logs da sincronização
│── README.md         # Documentação do projeto
└── requirements.txt  # Lista de dependências (se necessário)


🛠️ Possíveis Melhorias
🔹 Adicionar gráficos para visualizar tendências de leitura
🔹 Melhorar a interface gráfica com Tkinter avançado
🔹 Criar uma API para acesso remoto às leituras
