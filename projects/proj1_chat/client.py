from MySocket import *


def process_string(client_socket, string):
    string_list = string.split(" ")

    if string_list[0] == "/join":

        if len(string_list) < 2:

            error_msg = utils.SERVER_JOIN_REQUIRES_ARGUMENT + '\n'
            sys.stdout.write(error_msg)

        else:

            client_socket.send(pad_string(string))

    elif string_list[0] == "/create":

        if len(string_list) < 2:

            error_msg = utils.SERVER_CREATE_REQUIRES_ARGUMENT + '\n'
            sys.stdout.write(error_msg)

        else:           
            client_socket.send(pad_string(string))

    elif string_list[0] == "/list":
        client_socket.send(pad_string(string))

    elif string.startswith("/"):

        error_msg = utils.SERVER_INVALID_CONTROL_MESSAGE.format(string) + '\n'
        sys.stdout.write(error_msg)

    else:
        client_socket.send(pad_string(string))


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: python client.py <name> <host> <port>\n" +
            "python client.py Vincent localhost 12345")
        sys.exit(1)

    name = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])

    client_socket = MySocket(host, port, name, socket_list=[sys.stdin])
    client_socket.socket_list.append(client_socket)

    try:
        client_socket.connect()
        client_socket.send(pad_string(client_socket.name))
    except:

        error_msg = utils.CLIENT_CANNOT_CONNECT.format(client_socket.get_host(), client_socket.get_port()) + '\n'
        sys.stdout.write(error_msg)
        sys.exit(1)

    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
    sys.stdout.flush()

    while 1:
        ready_to_read, ready_to_write, in_error = select.select(client_socket.socket_list, [], [], 0)

        for socket in ready_to_read:

            if socket == client_socket:

                sys.stdout.write(utils.CLIENT_WIPE_ME)
                msg = client_socket.recv(utils.MESSAGE_LENGTH)

                if msg:

                    if msg.strip() == "":
                        msg = '\r'
                    else:
                        msg = '\r' + msg.strip() + '\n'
                    sys.stdout.write(msg)
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                    sys.stdout.flush()

                else:

                    error_msg = '\r' + utils.CLIENT_SERVER_DISCONNECTED.format(client_socket.get_host(), client_socket.get_port()) + '\n'
                    sys.stdout.write(error_msg)
                    sys.exit(1)

            else:
 
                string = sys.stdin.readline().strip()
                process_string(client_socket, string)
                sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                sys.stdout.flush()

    client_socket.close()
