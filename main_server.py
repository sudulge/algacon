import socket
import threading

HOST = ''
PORT = 50007


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            message = client.recv(1024)

            broadcast(message)

        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            break

def receive():
    while True:
        client, address = server.accept()
        # if len(clients) == 2:
        #     client.send("FULL".encode('utf-8'))
        #     continue
        print(f"connected with {address}")
        clients.append(client)
        broadcast(f"{client} joined".encode('utf-8'))
        client.send("connected to server".encode('utf-8'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()