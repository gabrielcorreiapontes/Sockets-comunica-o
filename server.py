import socket
import json

HOST = '127.0.0.1'
PORT = 65432

def handle_handshake(conn):
    data = conn.recv(1024).decode()
    print(f"Handshake recebido: {data}")
    
    try:
        handshake_data = json.loads(data)
        mode = handshake_data['mode']
        max_size = handshake_data['max_size']
        window_size = handshake_data["window_size'"]
        
        response = json.dumps({
            "type": "HANDSHAKE_RESPONSE",
            "status": "HANDSHAKE_OK",
            "mode": mode,
            "max_size": max_size
            "window_size": handshake_data ["windowsize"]
        })
        conn.sendall(response.encode())
        
        return mode, int(max_size)
    except json.JSONDecodeError:
        print("Erro: Handshake inválido")
        error_response = json.dumps({
            "type": "HANDSHAKE_RESPONSE",
            "status": "HANDSHAKE_ERROR"
        })
        conn.sendall(error_response.encode())
        return None, None

def handle_client(conn, addr, mode, max_size, window_size):
    print(f"Conectado por {addr}")
    print(f"Modo: {mode}, Tamanho máximo: {max_size}",janela : {window_size}")
    
    while True:
        try:
            data = conn.recv(max_size).decode()
            if not data:
                break
            
            message = json.loads(data)
            
            if message["type"] == "MESSAGE":
                seq = message["seq"]
                print(f"Mensagem recebida: {message['content']}")


                #Envio do ack para o cliente
                 ack = json.dumps({
                    "type": "ACK",
                    "seq": seq})

                     
                response = json.dumps({
                    "type": "RESPONSE",
                    "content": f"Servidor recebeu: {message['content']}"
                })
                conn.sendall(response.encode())
            
            elif message["type"] == "END":
                print("Cliente solicitou encerramento da conexão.")
                break
            
            else:
                print(f"Tipo de mensagem desconhecido: {message['type']}")
        
        except json.JSONDecodeError:
            print("Erro: mensagem inválida recebida.")
        except Exception as e:
            print(f"Erro na comunicação: {e}")
            break
    
    print(f"Conexão com {addr} encerrada")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escutando em {HOST}:{PORT}")
        
        while True:
            conn, addr = s.accept()
            with conn:
                mode, max_size = handle_handshake(conn)
                if mode and max_size:
                    handle_client(conn, addr, mode, max_size)

if __name__ == "__main__":
    start_server()
