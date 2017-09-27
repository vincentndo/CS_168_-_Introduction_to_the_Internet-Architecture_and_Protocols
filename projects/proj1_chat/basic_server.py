import sys
import socket

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python basic_server.py <port>\n" +
            "python basic_server.py 12345")
        sys.exit(1)

    port = int(sys.argv[1])

    server_socket = socket.socket()
    server_socket.bind( ("", port) )
    server_socket.listen(5)

    while True:
        (new_socket, address) = server_socket.accept()
        msg = new_socket.recv(1024)
        print(msg)
