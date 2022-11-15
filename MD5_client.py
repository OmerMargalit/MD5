"""
author: Omer Margalit
date: 7/11/2022
description: Get number that encrypt by MD5 and decrypt it
"""
import socket
import os
from threading import Thread
import hashlib

SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080
FLAG = [False, None]
CORES = os.cpu_count()
DATA_PER_CORE = 10000000


def hash_func(num, number_to_find):
    """
    :param num
    :param number_to_find
    :return: None
    """
    global FLAG
    global DATA_PER_CORE
    corret_num = int(num)
    for j in range(corret_num, corret_num + DATA_PER_CORE):
        if FLAG[0]:
            break
        x = str(j)
        result = hashlib.md5(x.encode()).hexdigest()
        if result == number_to_find:
            FLAG = [True, j]


def main():
    """
    The main function, conect to the server
    :return: None
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        while FLAG[0] is False:
            msg_to_server = 'begin' + str(CORES) + 'finish'
            client_socket.send(msg_to_server.encode())
            data = client_socket.recv(5).decode()
            number_to_find = ''
            while data == 'begin':
                while not data.endswith('finish'):
                    data += client_socket.recv(1).decode()
                number_to_find = data[5:-6]
            print(number_to_find)
            num = 0
            data = client_socket.recv(5).decode()
            print(data)
            while data == 'begin':
                while not data.endswith('finish'):
                    data += client_socket.recv(1).decode()
                data = data[5:-6]
                if data != 'done_search':
                    num = int(data)
                else:
                    client_socket.close()
                all_threads = []
                for i in range(0, CORES):
                    thread = Thread(target=hash_func, args=(num, number_to_find))
                    all_threads.append(thread)
                    thread.start()
                    num += 10000000
                for i in all_threads:
                    i.join()
                if True in FLAG:
                    msg_to_server = 'startfound' + str(FLAG[1]) + 'finish'
                    print(msg_to_server)
                    print('sent')
                    client_socket.send(msg_to_server.encode())
                else:
                    msg_to_server = 'STOP'
                    client_socket.send(msg_to_server.encode())
                    client_socket.close()
                    main()
    except socket.error as msg_to_server:
        print('error in communication with server - ' + str(msg_to_server))
    finally:
        client_socket.close()


if __name__ == '__main__':
    main()