"""
Author: Omer Margalit
Date: 7/11/2022
Description: The server send number that encrypt by MD5 function.
"""

import socket
from threading import Thread, Lock

LOCALHOST = "127.0.0.1"
ECnumber1 = 'EC9C0F7EDCC18A98B1F31853B1813301'
PORT = 8080
QUEUE_SIZE = 10
CORRECT_NUM = 0
CLIENT_LIST = {}
lock = Lock()
FLAG = False


def handle_connection(client_socket, client_address):
    """
    :param client_socket
    :param client_address
    :return: None
    """
    global FLAG
    global CORRECT_NUM
    global lock
    try:
        print('New connection received from ' + client_address[0] + ':' + str(client_address[1]))
        client_data = client_socket.recv(5).decode()
        while client_data == 'begin':
            while not client_data.endswith('finish'):
                client_data += client_socket.recv(1).decode()
        cores = client_data[5:-6]
        cores = int(cores)
        print(cores)
        CLIENT_LIST[client_socket] = cores
        msg = 'begin'
        msg += ECnumber1
        msg += 'finish'
        client_socket.send(msg.encode())
        if not FLAG:
            lock.acquire()
            msg = 'begin'
            msg += str(CORRECT_NUM)
            msg += 'finish'
            CORRECT_NUM += 10000000 * cores
            lock.release()
            client_socket.send(msg.encode())
            client_data = client_socket.recv(5).decode()
            while client_data == 'begin':
                while not client_data.endswith('finish'):
                    client_data += client_socket.recv(1).decode()
            if 'found' in client_data:
                for j in CLIENT_LIST.keys():
                    try:
                        j.send('STOP'.encode())
                    except socket.error:
                        pass
                FLAG = True
                print(client_data[10:-6])
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        client_socket.close()


def main():
    """
    The main loop
    :return: NONE
    """
    global FLAG
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((LOCALHOST, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)

        while not FLAG:
            client_socket, client_address = server_socket.accept()
            thread = Thread(target=handle_connection,
                            args=(client_socket, client_address))
            thread.start()

    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()