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

        base = 0
        next_seq = 0
        tempos_envio = {}

        tempo_inicio = time.time()

        while base < len(pacotes):
            if modo == "rs":
                pacote = pacotes[base]
                cliente.send((json.dumps(pacote) + "\n").encode())
                print(f"Enviado pacote {pacote['sequencia']} com checksum {pacote['checksum']}")
                tempos_envio[pacote["sequencia"]] = time.time()
                next_seq = base + 1  # só avança após ACK

            else:  # GBN
                while next_seq < base + janela and next_seq < len(pacotes):
                    pacote = pacotes[next_seq]
                    cliente.send((json.dumps(pacote) + "\n").encode())
                    print(f"Enviado pacote {pacote['sequencia']} com checksum {pacote['checksum']}")
                    tempos_envio[pacote["sequencia"]] = time.time()
                    next_seq += 1



            try:
                cliente.settimeout(2.5)
                resposta = cliente.recv(256).decode()
                linhas = resposta.strip().splitlines()

                for linha in linhas:
                    try:
                        ack = json.loads(linha)
                        seq = ack.get("sequencia", -1)

                        if ack["tipo"] == "ACK":
                            if seq in tempos_envio:
                                delta = time.time() - tempos_envio[seq]
                            else:
                                delta = 0

                            print(f"ACK cumulativo recebido até o pacote {seq} (RTT: {delta:.3f}s)")

                            if modo == "gbn":
                                # move a base apenas até o ACK cumulativo
                                base = seq + 1
                                next_seq = base  # reseta para a nova janela


                            elif modo == "rs":
                                if seq == base:
                                    base += 1
                                else:
                                    print("ACK fora de ordem.")

                        elif ack["tipo"] == "ERRO":
                            print(f"Erro no pacote {seq}, reenviando da base...")
                            if modo == "gbn":
                                next_seq = base  # Reenvia toda a janela
                    except json.JSONDecodeError:
                        print("Resposta inválida do servidor:", linha)

            except socket.timeout:
                print("Timeout! Reenviando a partir da base da janela.")
                if modo == "gbn":
                    next_seq = base


        tempo_fim = time.time()
        print(f"Tempo total de envio: {tempo_fim - tempo_inicio:.3f} segundos")

    cliente.close()

if __name__ == "__main__":
    main()

    #janela fixa, timer para cada ack e checksum no cliente.