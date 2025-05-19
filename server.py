import socket
import json
import random

ERRO_PROBABILIDADE = 0.2
PERDA_PROBABILIDADE = 0.15  



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

    buffer = ""
    recebidos = {}
    esperado = 0

    while True:
        try:
            data = conexao.recv(1024).decode()
            if not data:
                print("Conexão encerrada pelo cliente.")
                break
            buffer += data

            while "\n" in buffer:
                linha, buffer = buffer.split("\n", 1)
                if not linha.strip():
                    continue

                print("Pacote recebido:", linha)

                try:
                    pacote = json.loads(linha)
                except:
                    print("Erro no JSON recebido.")
                    continue

                if pacote["conteudo"] == "###" or pacote["sequencia"] == -1:
                    ack_msg = json.dumps({"tipo": "ACK", "sequencia": pacote["sequencia"]}) + "\n"
                    conexao.send(ack_msg.encode())

                    if recebidos:
                        final = ''.join(recebidos[k] for k in sorted(recebidos))
                        print("Mensagem reconstruída:", final)
                    else:
                        print("Fim recebido, mas nenhuma mensagem para reconstruir.")

                    recebidos = {}
                    esperado = 0
                    continue



                seq = pacote["sequencia"]
                conteudo = pacote["conteudo"]
                checksum_pacote = pacote["checksum"]
                # Simulação de perda: ignora o pacote com uma certa probabilidade
                if random.random() < PERDA_PROBABILIDADE:
                    print(f"[Servidor] ❌ Simulando perda do pacote {seq} — ignorado completamente")
                    continue  # ignora o pacote (nenhum ACK nem ERRO enviado)
                # Simulação de erro: altera o conteúdo com 20% de chance
                if random.random() < ERRO_PROBABILIDADE:
                    print(f"[Servidor] ⚠️ Simulando erro no pacote {seq}")
                    conteudo = conteudo[::-1]  # inverte o conteúdo (ou modifique qualquer coisa)


                if calcular_checksum(conteudo) != checksum_pacote:
                    print(f"Checksum errado no pacote {seq}")
                    erro_msg = json.dumps({"tipo": "ERRO", "sequencia": seq}) + "\n"
                    conexao.send(erro_msg.encode())
                    continue

                if tipo == "gbn":
                    if seq == esperado:
                        recebidos[seq] = conteudo
                        esperado += 1

                        # Verifica se completou uma janela de tamanho fixo
                        if esperado % 4 == 0 or pacote["conteudo"] == "###":
                            ack_msg = json.dumps({"tipo": "ACK", "sequencia": esperado - 1}) + "\n"
                            conexao.send(ack_msg.encode())
                            print(f"[Servidor] ✅ ACK cumulativo enviado até o pacote {esperado - 1}")
                    else:
                        print(f"Fora de ordem. Esperado {esperado}, recebeu {seq}")
                        # Ignora pacotes fora de ordem


                elif tipo == "rs":
                    recebidos[seq] = conteudo
                    ack_msg = json.dumps({"tipo": "ACK", "sequencia": seq}) + "\n"
                    conexao.send(ack_msg.encode())

        except Exception as e:
            print("Erro ao receber pacote:", e)
            break

    conexao.close()

if __name__ == "__main__":
    main()