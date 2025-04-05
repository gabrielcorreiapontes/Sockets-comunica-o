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
        
        response = json.dumps({
            "status": "HANDSHAKE_OK",
            "mode": mode,
            "max_size": max_size
        })
        conn.sendall(response.encode())
        
        return mode, int(max_size)
    except json.JSONDecodeError:
        print("Erro: Handshake inválido")
        conn.sendall(json.dumps({"status": "HANDSHAKE_ERROR"}).encode())
        return None, None

def handle_client(conn, addr, mode, max_size):
    print(f"Conectado por {addr}")
    print(f"Modo: {mode}, Tamanho máximo: {max_size}")
    
    while True:
        try:
            data = conn.recv(max_size).decode()
            if not data:
                break
            print(f"Recebido: {data}")
            
            response = f"Servidor recebeu: {data}"
            conn.sendall(response.encode())
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