import socket
import json
from time import sleep

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
    pacotes.append({"sequencia": len(blocos), "conteudo": "###", "checksum": 0})
    return pacotes

def gerar_checksum(dado):
    return sum(dado.encode()) % 256

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
    mensagem = input("Digite a mensagem para enviar: ")

    pacotes = criar_pacotes(mensagem)

    rajada = "True" if len(pacotes) > 1 else "False"
    cliente.send(f"{modo},{rajada}".encode())

    confirma = cliente.recv(256).decode()
    print("Servidor:", confirma)

    janela = 4
    inicio = 0
    proximo = 0

    while inicio < len(pacotes):
        while proximo < inicio + janela and proximo < len(pacotes):
            cliente.send(json.dumps(pacotes[proximo]).encode())
            print(f"Enviado pacote {pacotes[proximo]['sequencia']}")
            proximo += 1

        try:
            cliente.settimeout(2.5)
            resposta = cliente.recv(256).decode()
            print("Servidor respondeu:", resposta)

            if not resposta:
                print("Conexão encerrada.")
                break

            if modo == "gbn":
                if "ACK" in resposta:
                    recebidos = resposta.count("ACK")
                    inicio += recebidos
                    print(f"Janela movida para {inicio}")
                else:
                    print("Erro, reenviando desde o início da janela.")
                    proximo = inicio

            elif modo == "rs":
                if "ACK" in resposta:
                    inicio += 1
                    print(f"Pacote confirmado. Nova base {inicio}")
                else:
                    print("Erro detectado, mas continuando...")

        except socket.timeout:
            print("Timeout detectado! Reenviando...")
            proximo = inicio

    cliente.close()

if __name__ == "__main__":
    main()
