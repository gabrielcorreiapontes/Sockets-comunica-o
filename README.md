# 💬 Projeto de Comunicação via Sockets - Redes de Computadores

Este projeto foi desenvolvido como parte de um trabalho prático da disciplina de **Infraestrutura de Redes e Comunicação**. A aplicação simula a troca de mensagens entre cliente e servidor utilizando **sockets TCP em Python**, com foco em uma comunicação confiável, onde **não há perdas ou erros no canal de comunicação**.

## 📌 Objetivo da Etapa Atual

Implementar a troca de mensagens entre cliente e servidor considerando um **canal de comunicação perfeito** (sem erros ou perdas).

## ⚙️ Tecnologias Utilizadas

- Python 3.x
- Biblioteca `socket` (nativa do Python)
- Biblioteca `json` (para estruturação das mensagens)
- Protocolo de transporte: **TCP/IP**

## 📁 Estrutura do Projeto


sockets2025.1/
├── client.py         # Código do cliente socket
├── server.py         # Código do servidor socket
├── README.md         # Documentação do projeto


## 🔄 Funcionamento

1. O **servidor** é iniciado e escuta em uma porta local (`127.0.0.1:65432`).
2. O **cliente** se conecta ao servidor.
3. O cliente envia uma mensagem de **handshake**, informando o modo de operação e o tamanho máximo de pacote.
4. O servidor responde confirmando o handshake.
5. Cliente e servidor entram em modo de **troca de mensagens** (formato JSON).
6. O cliente pode encerrar a conexão enviando um pacote do tipo `"END"`.

## 📤 Estrutura das Mensagens

Todas as mensagens trocadas são em formato **JSON**.

### 🔹 Handshake
json
{
  "mode": "NORMAL",
  "max_size": 1024
}


### 🔹 Mensagem de Texto
json
{
  "type": "MESSAGE",
  "content": "Olá, servidor!"
}


### 🔹 Encerramento
json
{
  "type": "END"
}


## ▶️ Como Executar

### 1. Iniciar o servidor

bash
python server.py


### 2. Em outro terminal, iniciar o cliente

bash
python client.py


### 3. Trocar mensagens

Digite qualquer mensagem no terminal do cliente e veja a resposta do servidor.  
Para encerrar a conexão, digite `sair`.

## 🧪 Exemplo de Execução

### Cliente

Conectado ao servidor 127.0.0.1:65432
Handshake bem-sucedido
Digite uma mensagem (ou 'sair' para encerrar): Olá!
Resposta do servidor: Servidor recebeu: Olá!
Digite uma mensagem (ou 'sair' para encerrar): sair
Conexão encerrada


### Servidor

Servidor escutando em 127.0.0.1:65432
Handshake recebido: {"mode": "NORMAL", "max_size": 1024}
Conectado por ('127.0.0.1', 54213)
Modo: NORMAL, Tamanho máximo: 1024
Mensagem recebida: Olá!
Cliente solicitou encerramento da conexão.
Conexão com ('127.0.0.1', 54213) encerrada


## 🧠 Aprendizados e Conceitos Aplicados

- Comunicação cliente-servidor com `socket.socket`
- Handshake inicial com validação de modo e tamanho
- Estruturação de dados com JSON
- Comunicação confiável via TCP
- Encerramento seguro da conexão

## 📅 Próximas Etapas

- Implementar modos diferentes de operação conforme o parâmetro `mode`
- Adicionar simulação de canal com erros (checksum, retransmissão)
- Suporte a múltiplos clientes com `threading` ou `asyncio`

## 👥 Autores

- Ester Carvalho
- Paulo Ricardo
- Luiz Flavius Veras
- Gabriel Pontes
- Arthur Borgis
- João Lucas

## 📄 Licença

Este projeto é de uso educacional, desenvolvido como atividade da disciplina de Redes de Computadores.
