import socket
import json

HOST = '127.0.0.1'
PORT = 65432

def perform_handshake(sock, mode, max_size):
    handshake_data = json.dumps({
        "mode": mode,
        "max_size": max_size
    })
    sock.sendall(handshake_data.encode())
    
    response = sock.recv(1024).decode()
    response_data = json.loads(response)
    
    if response_data.get('status') == "HANDSHAKE_OK":
        print("Handshake bem-sucedido")
        return True
    else:
        print("Erro no handshake")
        return False

def start_client():
    mode = "NORMAL"
    max_size = 1024
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"Conectado ao servidor {HOST}:{PORT}")
        
        if perform_handshake(s, mode, max_size):
            while True:
                message = input("Digite uma mensagem (ou 'sair' para encerrar): ")
                if message.lower() == 'sair':
                    end_message = json.dumps({
                        "type": "END"
                    })
                    s.sendall(end_message.encode())
                    break
                
                message_data = json.dumps({
                    "type": "MESSAGE",
                    "content": message
                })
                s.sendall(message_data.encode())
                
                data = s.recv(max_size).decode()
                response = json.loads(data)
                
                if response["type"] == "RESPONSE":
                    print(f"Resposta do servidor: {response['content']}")
        
        print("Conexão encerrada")

if __name__ == "__main__":
    start_client()
