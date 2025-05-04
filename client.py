import socket
import json
import time

def criar_pacotes(texto):
    blocos = [texto[i:i+3] for i in range(0, len(texto), 3)]
    pacotes = []
    for idx, bloco in enumerate(blocos):
        pacote = {
            "sequencia": idx,
            "conteudo": bloco,
            "checksum": sum(bloco.encode()) % 256
        }
        pacotes.append(pacote)
    return pacotes

def escolher_modo():
    while True:
        escolha = input("Escolha modo (1=GBN, 2=RS): ")
        if escolha == "1":
            return "gbn"
        elif escolha == "2":
            return "rs"
        else:
            print("Opção inválida.")

def main():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('localhost', 2048))

    modo = escolher_modo()
    rajada = "True"

    cliente.send(f"{modo},{rajada}".encode())
    confirma = cliente.recv(256).decode()
    print("Servidor:", confirma)

    janela = 4
    while True:
        mensagem = input("Digite a mensagem para enviar (ou 'exit' para encerrar): ")
        if mensagem.strip().lower() == "exit":
            fim = json.dumps({"sequencia": -1, "conteudo": "###", "checksum": 0}) + "\n"
            cliente.send(fim.encode())
            break

        pacotes = criar_pacotes(mensagem)
        pacotes.append({"sequencia": len(pacotes), "conteudo": "###", "checksum": 0})

        inicio = 0
        proximo = 0
        tempo_inicio = time.time()

        while inicio < len(pacotes):
            if modo == "rs":
                cliente.send((json.dumps(pacotes[inicio]) + "\n").encode())
                print(f"Enviado pacote {pacotes[inicio]['sequencia']}")
                proximo = inicio + 1  # só avança após ACK abaixo
            else:  # modo gbn
                while proximo < inicio + janela and proximo < len(pacotes):
                    cliente.send((json.dumps(pacotes[proximo]) + "\n").encode())
                    print(f"Enviado pacote {pacotes[proximo]['sequencia']}")
                    proximo += 1


            try:
                cliente.settimeout(2.5)
                resposta = cliente.recv(256).decode()
                linhas = resposta.strip().splitlines()

                for linha in linhas:
                    try:
                        ack = json.loads(linha)
                        if ack["tipo"] == "ACK":
                            if modo == "gbn":
                                print(f"ACK recebido: {ack['sequencia']}")
                                inicio = ack["sequencia"] + 1
                                proximo = inicio
                                print(f"Janela movida para {inicio}")
                            elif modo == "rs":
                                if ack["sequencia"] == inicio:
                                    print(f"ACK recebido: {ack['sequencia']}")
                                    inicio += 1
                                else:
                                    print("ACK fora de ordem.")
                        elif ack["tipo"] == "ERRO":
                            print(f"Erro no pacote {ack['sequencia']}, reenviando da base...")
                            proximo = inicio
                    except json.JSONDecodeError:
                        print("Resposta inválida do servidor:", linha)

            except socket.timeout:
                print("Timeout! Reenviando a partir da base da janela.")
                proximo = inicio

        tempo_fim = time.time()
        print(f"Tempo total de envio: {tempo_fim - tempo_inicio:.3f} segundos")

    cliente.close()

if __name__ == "__main__":
    main()