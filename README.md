# 💬 Projeto de Comunicação via Sockets - Redes de Computadores

Este projeto foi desenvolvido como parte de um trabalho prático da disciplina de **Infraestrutura de Redes e Comunicação**. A aplicação simula a troca de mensagens entre cliente e servidor utilizando **sockets TCP em Python**, com foco em **comunicação confiável**, incluindo a simulação de **erros e perdas no canal de comunicação**.

## 📌 Objetivo da Etapa Atual
 
Implementar a troca de mensagens entre cliente e servidor considerando:

1. Um **canal perfeito** (sem erros ou perdas);
2. A **simulação de falhas** (erros e perdas) para testar a robustez do protocolo;
3. O **comportamento correto** dos protocolos de retransmissão, com destaque para os modos GBN (Go-Back-N) e RS (Stop-and-Wait).

## ⚙️ Tecnologias Utilizadas

* Python 3.x
* Biblioteca `socket` (nativa do Python)
* Biblioteca `json` (para estruturação das mensagens)
* Protocolo de transporte: **TCP/IP**

## 📁 Estrutura do Projeto

```
sockets2025.1/
├── client.py         # Código do cliente socket
├── server.py         # Código do servidor socket
├── README.md         # Documentação do projeto
```

## 🔄 Funcionamento

1. O **servidor** é iniciado e escuta na porta `localhost:2048`.
2. O **cliente** se conecta ao servidor.
3. O cliente envia uma mensagem de **handshake**, contendo:

   * modo de operação (`gbn` ou `rs`)
   * parâmetro de rajada (não utilizado nesta etapa)
   * ativação de simulação de falhas (`sim` ou `nao`)
4. O servidor responde confirmando o handshake.
5. Cliente e servidor trocam mensagens em formato JSON.
6. Ao final, o cliente envia um pacote especial de encerramento (`###`).

## 📤 Estrutura das Mensagens

Todas as mensagens trocadas são em formato **JSON**, separadas por `\n`.

### 🔹 Handshake

```
modo,rajada,sim|nao
```

### 🔹 Pacote de Dados

```json
{
  "sequencia": 2,
  "conteudo": "abc",
  "checksum": 123
}
```

### 🔹 ACK

```json
{
  "tipo": "ACK",
  "sequencia": 2
}
```

### 🔹 ERRO

```json
{
  "tipo": "ERRO",
  "sequencia": 2
}
```

### 🔹 Encerramento

```json
{
  "sequencia": -1,
  "conteudo": "###",
  "checksum": 0
  // Este pacote especial é utilizado para indicar o fim da transmissão da mensagem pelo cliente
}
```

## ▶️ Como Executar

### 1. Iniciar o servidor

```bash
python server.py
```

### 2. Em outro terminal, iniciar o cliente

```bash
python client.py
```

### 3. Interagir com o sistema

* Informe o modo desejado (1 para GBN ou 2 para RS)
* Ative ou não a simulação de falhas (s para sim / qualquer outra tecla para não)
* Digite a mensagem e acompanhe a troca de pacotes com ou sem erros

## 🧪 Simulação de Erros e Perdas

* **Erros**: Simulados por alteração no conteúdo para quebrar o checksum.
* **Perdas**: Simuladas ignorando pacotes aleatoriamente.
* O cliente deve retransmitir pacotes com erro ou perdidos com base no protocolo selecionado (GBN ou RS).

## 🧠 Aprendizados e Conceitos Aplicados

* Comunicação cliente-servidor com `socket.socket`
* Handshake inicial com parâmetros operacionais
* Protocolos de confiabilidade (GBN e RS)
* Estruturação de pacotes com JSON
* Simulação de falhas (erros e perdas) com comportamento controlado
* Controle de janelas de envio e confirmação com ACKs

## 📅 Próximas Etapas

* Suporte a múltiplos clientes com `threading` ou `asyncio`
* Interface gráfica para visualização da transmissão de pacotes
* Logs persistentes e análises de desempenho por modo

## 👥 Autores

* Ester Carvalho
* Paulo Ricardo
* Luiz Flavius Veras
* Gabriel Pontes
* Arthur Borgis
* João Lucas

## 📄 Licença

Este projeto é de uso educacional, desenvolvido como atividade da disciplina de Redes de Computadores.
