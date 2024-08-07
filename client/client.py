import socket
import json
import logging
import threading
import sys

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65432

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

def authenticate(client_socket, auth_key):
    auth_message = {
        "type": "AUTH",
        "payload": {
            "authKey": auth_key
        }
    }
    client_socket.sendall(json.dumps(auth_message).encode())

    response = client_socket.recv(1024).decode()
    logging.debug(f"Received authentication response: {response}")
    response_message = json.loads(response)

    if response_message.get("type") == "AUTH_CONFIRMED":
        logging.info("Authentication successful")
        return True
    else:
        logging.error("Authentication failed")
        return False

def handle_server_response(client_socket):
    while True:
        try:
            response = client_socket.recv(1024).decode()
            if not response:
                break

            print("\n" + "-"*20)
            logging.debug(f"Received from server: {response}")
            message = json.loads(response)

            if message["type"] == "FILE_CONTENT":
                print("\nFile content received:")
                print(message["payload"])

            elif message["type"] == "UPDATE_CONFIRMED":
                print(f"\nUpdate confirmed: Line {message['payload']['line']} updated with new content.")

            elif message["type"] == "UPDATE":
                print(f"\nBroadcast update: Line {message['payload']['line']} updated with new content.")

            elif message["type"] == "ERROR":
                print(f"\nError: {message['payload']}")

            sys.stdout.write("\nEnter command (VIEW, UPDATE <line_number> <content>): ")

        except Exception as e:
            logging.error(f"Error handling server response: {e}")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    auth_key = input("Enter the authentication key: ")

    if authenticate(client_socket, auth_key):
        threading.Thread(target=handle_server_response, args=(client_socket,), daemon=True).start()

        print("Enter command (VIEW, UPDATE <line_number> <content>): ", end='')

        while True:
            sys.stdout.flush()
            command = input()
            if command.startswith("VIEW"):
                request = {"type": "VIEW", "payload": {}}
                client_socket.sendall(json.dumps(request).encode())

            elif command.startswith("UPDATE"):
                try:
                    _, line, content = command.split(maxsplit=2)
                    line = int(line)
                    request = {
                        "type": "UPDATE",
                        "payload": {
                            "line": line,
                            "content": content
                        }
                    }
                    client_socket.sendall(json.dumps(request).encode())
                except ValueError:
                    print("Invalid command format. Use: UPDATE <line_number> <content>")

            else:
                print("Unknown command. Use 'VIEW' to view file or 'UPDATE <line_number> <content>' to update.")

    client_socket.close()

main()
