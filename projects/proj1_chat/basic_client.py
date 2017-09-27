import sys
import socket

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python basic_client.py <host> <port>\n" +
            "python basic_client.py localhost 12345")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    client_socket = socket.socket()
    client_socket.connect( (host, port) )

    msg = raw_input()
    client_socket.send(msg)
    sys.exit(0)