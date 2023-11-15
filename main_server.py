# TODO: multiplay.: 연결한 클라이언트가 또 연결 시도할 경우 무시. or 기존연결끊고 새로연결

import socket
import threading
import random
import time

HOST = ''
PORT = 50007


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

def broadcast(message, from_client=None):
    for client in clients:
        if client == from_client:
            continue
        client.send(message)
        print(message)


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            
            broadcast(message, client)

        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            break

def receive():
    while True:
        client, address = server.accept()
        if len(clients) == 2:
            client.send("FULL".encode('utf-8'))
            continue
        print(f"connected with {address}")
        clients.append(client)
        broadcast(f"{client} joined".encode('utf-8'))
        client.send("connected to server".encode('utf-8'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

        if len(clients) == 2:
            print('gamestart')
            time.sleep(0.5)
            broadcast("GAMESTART".encode('utf-8'))
            thread = threading.Thread(target=game_loop, args=())
            thread.start()
            continue


def generate_objects(name, speed, position):
    broadcast(f"GENERATE {name} {str(speed)} {','.join(map(str, position))} ".encode('utf-8'))

def game_loop():

    # 타이머 설정
    start_ticks = time.time()

    running = True

    while running:
        # 게임 시작 후 경과 시간 
        elapsed_time = int(time.time() - start_ticks)


        # 한번에 등장하는 운석 개수
        occur_of_default_rocks = 3 + int(elapsed_time // 20)
        occur_of_split_rocks = occur_of_default_rocks - 1
        occur_of_unbreakable_rocks = occur_of_default_rocks - 2
        min_rock_speed = 3 + int(elapsed_time // 20)
        max_rock_speed = 3 + int(elapsed_time // 10)

        probablity_num = random.randint(1, 1000)
        # 운석, 아이템 등장 확률 조정
        t = ''
        if probablity_num > 990:  # 10 / 1000  1%
            for i in range(2):
                for j in range(occur_of_default_rocks):
                    speed = random.randint(min_rock_speed, max_rock_speed)
                    position = (random.randint(i*840, (i+1)*840), 0)
                    # generate_objects('rock', speed, position)
                    t += f"/rock {str(speed)} {position[0]},{position[1]}"
            broadcast(t.encode('utf-8'))

        elif probablity_num > 985:  # 5 / 1000  0.5%
            for i in range(2):
                for j in range(occur_of_split_rocks):
                    speed = random.randint(min_rock_speed, max_rock_speed)
                    position = (random.randint(i*840, (i+1)*840), 0)
                    # generate_objects('splitrock', speed, position)
                    t += f"/splitrock {str(speed)} {position[0]},{position[1]}"
            broadcast(t.encode('utf-8'))
                
        elif probablity_num > 980:  # 5 / 1000  0.5%
            for i in range(2):
                for j in range(occur_of_unbreakable_rocks):
                    speed = random.randint(min_rock_speed, max_rock_speed)
                    position = (random.randint(i*840, (i+1)*840), 0)
                    # generate_objects('unbreakablerock', speed, position)
                    t += f"/unbreakablerock {str(speed)} {position[0]},{position[1]}"
            broadcast(t.encode('utf-8'))

        elif probablity_num > 978:  # 2 / 1000  0.2%
            for i in range(2):
                position = (random.randint(i*840, (i+1)*840), 0)
                # generate_objects('heal', 20, position)
                t += f"/heal 20 {position[0]},{position[1]}"
            broadcast(t.encode('utf-8'))

        elif probablity_num > 973:  # 5 / 1000  0.5% 
            for i in range(2):
                position = (random.randint(i*840, (i+1)*840), 0)
                # generate_objects('speedup', 20, position)
                t += f"/speedup 20 {position[0]},{position[1]}"
            broadcast(t.encode('utf-8'))

        elif probablity_num > 970:
            for i in range(2):
                position = (random.randint(i*840, (i+1)*840), 0)
                # generate_objects('powerup', 20, position)
                t += f"/powerup 20 {position[0]},{position[1]}"
            broadcast(t.encode('utf-8'))

    # fps_clock.tick(60)
        time.sleep(0.06)
        
receive()