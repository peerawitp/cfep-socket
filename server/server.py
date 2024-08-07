import socket
import threading
import json
import logging
import secrets

HOST = '127.0.0.1'
PORT = 65432
FILE_PATH = 'shared_file.txt'
VERBOSE = True

GLOBAL_AUTH_KEY = secrets.token_hex(16)
print(f"Server Auth Key: {GLOBAL_AUTH_KEY}")

logging.basicConfig(level=logging.DEBUG if VERBOSE else logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

clients = set()
auth_clients = {}

def read_file():
    with open(FILE_PATH, 'r') as file:
        return file.read()

def update_file(line, new_content):
    with open(FILE_PATH, 'r+') as file:
        lines = file.readlines()
        if line < 0:
            raise ValueError("Invalid line number")
        elif line < len(lines):
            lines[line] = new_content + "\n"
        else:
            with open(FILE_PATH, 'a') as file:
                for _ in range(len(lines), line):
                    file.write("\n")
                file.write(new_content + "\n")
        with open(FILE_PATH, 'w') as file:
            file.writelines(lines)

def handle_client(client_socket):
    global clients, auth_clients
    client_address = client_socket.getpeername()
    clients.add(client_socket)
    logging.info(f"Client connected: {client_address}")

    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            logging.debug(f"Received data: {data}")
            message = json.loads(data)

            if message.get("type") == "AUTH":
                auth_key = message.get("payload", {}).get("authKey")
                if auth_key == GLOBAL_AUTH_KEY:
                    auth_clients[client_socket] = auth_key
                    response = {"type": "AUTH_CONFIRMED"}
                    logging.info(f"Client {client_address} authenticated successfully")
                    client_socket.sendall(json.dumps(response).encode())
                    break
                else:
                    response = {"type": "AUTH_FAILED"}
                    logging.error(f"Client {client_address} failed authentication")
                    client_socket.sendall(json.dumps(response).encode())
                    client_socket.close()
                    return
            else:
                response = {"type": "ERROR", "payload": "Authentication required"}
                client_socket.sendall(json.dumps(response).encode())
                return

        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            logging.debug(f"Received data: {data}")
            message = json.loads(data)
            response = {}

            if message["type"] == "VIEW":
                file_content = read_file()
                response = {"type": "FILE_CONTENT", "payload": file_content}
                logging.info(f"Sent file content to {client_address}")

            elif message["type"] == "UPDATE":
                if client_socket not in auth_clients:
                    response = {"type": "ERROR", "payload": "Authentication required"}
                    client_socket.sendall(json.dumps(response).encode())
                    continue

                line = message["payload"]["line"] - 1
                new_content = message["payload"]["content"]

                try:
                    update_file(line, new_content)
                    response = {"type": "UPDATE_CONFIRMED", "payload": {"line": line + 1, "content": new_content}}
                    logging.info(f"Updated line {line + 1} with new content: {new_content}")

                    for client in clients:
                        if client != client_socket:
                            try:
                                client.sendall(json.dumps({
                                    "type": "UPDATE",
                                    "payload": {"line": line + 1, "content": new_content}
                                }).encode())
                            except Exception as e:
                                logging.error(f"Error sending update to client: {e}")
                                clients.remove(client)
                except ValueError as e:
                    response = {"type": "ERROR", "payload": str(e)}
                    logging.error(f"Error updating file: {e}")

            else:
                response = {"type": "ERROR", "payload": "Invalid request type"}
                logging.error(f"Received invalid request type: {message['type']}")

            client_socket.sendall(json.dumps(response).encode())
            logging.debug(f"Sent response: {response}")

    except Exception as e:
        response = {"type": "ERROR", "payload": str(e)}
        client_socket.sendall(json.dumps(response).encode())
        logging.error(f"Exception occurred: {e}")

    finally:
        client_socket.close()
        clients.discard(client_socket)
        auth_clients.pop(client_socket, None)
        logging.info(f"Client disconnected: {client_address}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

start_server()
