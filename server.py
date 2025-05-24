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
        valores = inicial.strip().split(",")
        tipo = valores[0]
        rajada = valores[1]
        falhas = valores[2] if len(valores) > 2 else "nao"

    except:
        print("Erro ao interpretar configurações.")
        conexao.close()
        return

    print(f"Modo de operação: {tipo}")
    conexao.send(b"Configuracao aceita.\n")

    buffer = ""
    recebidos = {}
    esperado = 0

    ultimo_ack = -1

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

                    if all(k in recebidos for k in range(len(recebidos))):
                        final = ''.join(recebidos[k] for k in sorted(recebidos))
                        print("Mensagem reconstruída:", final)
                    else:
                        print("Nem todos os pacotes válidos foram recebidos — reconstrução incompleta.")


                    recebidos = {}
                    esperado = 0
                    continue



                seq = pacote["sequencia"]
                conteudo = pacote["conteudo"]
                checksum_pacote = pacote["checksum"]
                # Simulação de perda: ignora o pacote com uma certa probabilidade
                if falhas == "sim" and random.random() < PERDA_PROBABILIDADE:
                    print(f"[Servidor] ❌ Simulando perda do pacote {seq}")
                    continue  # ignora o pacote completamente

                conteudo_original = pacote["conteudo"]
                conteudo_para_verificacao = conteudo_original

                # Simula erro apenas na cópia usada para verificação
                if falhas == "sim" and random.random() < ERRO_PROBABILIDADE:
                    print(f"[Servidor] ⚠️ Simulando erro no pacote {seq}")
                    conteudo_para_verificacao = conteudo_para_verificacao[::-1] + "#"


                # Verifica integridade usando a cópia alterada (se necessário)
                if calcular_checksum(conteudo_para_verificacao) != checksum_pacote:
                    print(f"Checksum errado no pacote {seq}")
                    erro_msg = json.dumps({"tipo": "ERRO", "sequencia": seq}) + "\n"
                    conexao.send(erro_msg.encode())
                    continue

                # A partir daqui, usa o conteúdo original (sem alteração)
                conteudo = conteudo_original

                if tipo == "gbn":
                    if seq == esperado:
                        recebidos[seq] = conteudo
                        esperado += 1

                        # Após aceitar o esperado, verifique se os próximos já foram recebidos e avance
                        while esperado in recebidos:
                            esperado += 1

                        if esperado - 1 != ultimo_ack:
                            ack_msg = json.dumps({"tipo": "ACK", "sequencia": esperado - 1}) + "\n"
                            conexao.send(ack_msg.encode())
                            print(f"[Servidor] ✅ ACK cumulativo enviado até o pacote {esperado - 1}")
                            ultimo_ack = esperado - 1

                    else:
                        # Salva pacotes futuros, mas só envia ACK quando chegar o esperado
                        if seq > esperado:
                            recebidos[seq] = conteudo
                        print(f"[Servidor] 🛑 Ignorado: fora de ordem. Esperado {esperado}, recebeu {seq}")

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