import socket
import json

def calcular_checksum(dado):
    return sum(dado.encode()) % 256

def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('localhost', 2048))
    servidor.listen(3)

    print("Servidor aguardando conexão na porta 2048...")
    conexao, addr = servidor.accept()
    print(f"Conectado a {addr}")

    inicial = conexao.recv(256).decode()
    try:
        tipo, rajada = inicial.strip().split(",")
    except:
        print("Erro ao interpretar configurações.")
        conexao.close()
        return

    print(f"Modo de operação: {tipo}")
    conexao.send(b"Configuracao aceita.\n")

    recebidos = {}
    esperado = 0

    while True:
        try:
            pacote_bruto = conexao.recv(1024).decode()
            if not pacote_bruto:
                break
        except:
            break

        print("Pacote recebido:", pacote_bruto)

        try:
            pacote = json.loads(pacote_bruto)
        except:
            print("Erro no JSON recebido.")
            continue

        if pacote["conteudo"] == "###":
            break

        seq = pacote["sequencia"]
        conteudo = pacote["conteudo"]
        checksum_pacote = pacote["checksum"]

        if calcular_checksum(conteudo) != checksum_pacote:
            print(f"Checksum errado no pacote {seq}")
            conexao.send(b"ERRO")
            continue

        if tipo == "gbn":
            if seq == esperado:
                recebidos[seq] = conteudo
                esperado += 1
                conexao.send(b"ACK")
            else:
                print(f"Fora de ordem. Esperado {esperado}, recebeu {seq}")
                conexao.send(b"ERRO")

        elif tipo == "rs":
            recebidos[seq] = conteudo
            conexao.send(b"ACK")

    final = ''.join(recebidos[k] for k in sorted(recebidos))
    print("Mensagem reconstruída:", final)

    conexao.close()

if __name__ == "__main__":
    main()
