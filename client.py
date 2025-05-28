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
        print(f"[DEBUG] Criado pacote {idx}: '{bloco}' | Checksum: {sum(bloco.encode()) % 256}")
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

    falhas = input("Deseja ativar simulação de perda e erro? (s para sim / qualquer outra tecla para não): ")
    falhas = "sim" if falhas.strip().lower() == "s" else "nao"

    cliente.send(f"{modo},{rajada},{falhas}".encode())
    confirma = cliente.recv(256).decode()
    print("Servidor:", confirma)

    janela = 4
    while True:
        # Verifica se o usuário deseja encerrar
        saida = input("Deseja enviar uma mensagem? (s para sim, qualquer outra tecla para sair): ")
        if saida.strip().lower() != "s":
            fim = json.dumps({"sequencia": -1, "conteudo": "###", "checksum": 0}) + "\n"
            cliente.send(fim.encode())
            break

        # Define o tamanho da mensagem permitido
        while True:
            try:
                tamanho_msg = int(input("Digite o tamanho máximo da mensagem: "))
                break
            except ValueError:
                print("Por favor, digite um número inteiro válido.")

        # Solicita a mensagem e garante que esteja dentro do tamanho permitido
        mensagem = input("Digite a mensagem a ser enviada: ")
        while len(mensagem) > tamanho_msg:
            print(f"A mensagem tem {len(mensagem)} caracteres, mas o limite é {tamanho_msg}.")
            mensagem = input("Digite novamente a mensagem: ")


        pacotes = criar_pacotes(mensagem)
        pacotes.append({"sequencia": len(pacotes), "conteudo": "###", "checksum": 0})
        num_pacotes = len(pacotes)  # já inclui o pacote de término "###"
        print(f"[Cliente] Janela: {janela} | Total de pacotes a enviar: {num_pacotes}")


        base = 0
        next_seq = 0
        tempos_envio = {}

        tempo_inicio = time.time()

        while base < len(pacotes):
            if modo == "rs":
                pacote = pacotes[base]
                cliente.send((json.dumps(pacote) + "\n").encode())
                print(f"[Cliente] ➡️ Enviado pacote {pacote['sequencia']} | Payload: '{pacote['conteudo']}' | Checksum: {pacote['checksum']}")
                tempos_envio[pacote["sequencia"]] = time.time()
                next_seq = base + 1  # só avança após ACK

            else:  # GBN
                while next_seq < base + janela and next_seq < len(pacotes):
                    pacote = pacotes[next_seq]
                    cliente.send((json.dumps(pacote) + "\n").encode())
                    print(f"[Cliente] ➡️ Enviado pacote {pacote['sequencia']} | Payload: '{pacote['conteudo']}' | Checksum: {pacote['checksum']}")
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

                            print(f"[Cliente] ✅ ACK recebido para o pacote {seq} | Tempo de entrega: {delta:.3f}s")

                            if modo == "gbn":
                                if seq >= base:
                                    base = seq + 1
                                    next_seq = base



                            elif modo == "rs":
                                if seq == base:
                                    base += 1
                                else:
                                    print("ACK fora de ordem.")
                                    
                        elif ack["tipo"] == "ERRO":
                            if modo == "gbn":
                                print(f"[Cliente] ❗ Erro detectado no pacote {seq}, reiniciando envio a partir dele")
                                next_seq = seq  # Reinicia a janela do ponto do erro


                    except json.JSONDecodeError:
                        print("Resposta inválida do servidor:", linha)

            except socket.timeout:
                print(f"[Cliente] ⏱ Timeout! Reenviando todos os pacotes da janela a partir do pacote {base}")
                if modo == "gbn":
                    next_seq = base  # Redefine o next_seq para começar reenvio

            # Aguarda todos os ACKs dos pacotes reais antes de enviar o de término
            if modo == "gbn":
                while base < len(pacotes) - 1:
                    try:
                        cliente.settimeout(2.5)
                        resposta = cliente.recv(256).decode()
                        linhas = resposta.strip().splitlines()
                        for linha in linhas:
                            ack = json.loads(linha)
                            if ack["tipo"] == "ACK":
                                seq = ack["sequencia"]
                                if seq >= base:
                                    base = seq + 1
                                    next_seq = base
                    except socket.timeout:
                        next_seq = base
                        for i in range(base, min(base + janela, len(pacotes) - 1)):
                            pacote = pacotes[i]
                            cliente.send((json.dumps(pacote) + "\n").encode())
                            print(f"[Cliente] 🔁 Reenviado pacote {pacote['sequencia']} por timeout antes de término")
                            tempos_envio[pacote["sequencia"]] = time.time()

            # Agora sim envia o pacote de término
            pacote_final = pacotes[-1]
            cliente.send((json.dumps(pacote_final) + "\n").encode())
            print(f"[Cliente] 🏁 Enviado pacote final {pacote_final['sequencia']} | Payload: '###'")



        tempo_fim = time.time()
        print(f"Tempo total de envio: {tempo_fim - tempo_inicio:.3f} segundos")

    cliente.close()

if __name__ == "__main__":
    main()

