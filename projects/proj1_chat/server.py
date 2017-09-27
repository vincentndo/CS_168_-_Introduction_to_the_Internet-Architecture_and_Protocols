from MySocket import *


def broadcast(server_socket, socket, msg):

    if socket not in server_socket.client_dict:
        return

    client_name = server_socket.client_dict[socket][0]
    client_channel = server_socket.client_dict[socket][1]

    for s in server_socket.channel_dict[client_channel]:
        if server_socket.client_dict[s][0] != client_name:
            s.send(pad_string(msg))


def process_string(server_socket, socket, string):
    string_list = string.split(" ")

    if string_list[0] == "/join" :

        client_channel = " ".join(string_list[1:])
        client_name = client_names[socket]

        if client_channel in server_socket.channel_dict:

            if socket in server_socket.channel_dict[client_channel]:
                pass
            else:

                if socket in server_socket.client_dict:

                    msg = utils.SERVER_CLIENT_LEFT_CHANNEL.format(client_name)
                    broadcast(server_socket, socket, msg)
                    old_client_channel = server_socket.client_dict[socket][1]
                    server_socket.channel_dict[old_client_channel].remove(socket)

                server_socket.channel_dict[client_channel].add(socket)
                server_socket.client_dict[socket] = (client_name, client_channel)
                msg = utils.SERVER_CLIENT_JOINED_CHANNEL.format(client_name)
                broadcast(server_socket, socket, msg)

        else:

            error_msg = utils.SERVER_NO_CHANNEL_EXISTS.format(client_channel)
            socket.send(pad_string(error_msg))
        # print(server_socket.channel_dict)
        # print(server_socket.client_dict)

    elif string_list[0] == "/create":

        client_channel = " ".join(string_list[1:])
        client_name = client_names[socket]

        if client_channel in server_socket.channel_dict:

            error_msg = utils.SERVER_CHANNEL_EXISTS.format(client_channel)
            socket.send(pad_string(error_msg))

        else:
            server_socket.channel_dict[client_channel] = set([socket])

            if socket in server_socket.client_dict:

                old_client_channel = server_socket.client_dict[socket][1]
                server_socket.channel_dict[old_client_channel].remove(socket)

            server_socket.client_dict[socket] = (client_name, client_channel)
        # print(server_socket.channel_dict)
        # print(server_socket.client_dict)

    elif string_list[0] == "/list":
        all_channels = server_socket.channel_dict.keys()
        all_channels.sort()
        msg = ""
        for channel in all_channels:
            msg += channel + '\n'
        socket.send(pad_string(msg))

    else:

        # print client_names
        # print server_socket.socket_list
        # print server_socket.client_dict
        if socket in server_socket.client_dict:

            client_name = server_socket.client_dict[socket][0]
            client_channel = server_socket.client_dict[socket][1]
            msg = '[' + client_name + '] ' + string
            broadcast(server_socket, socket, msg)

        else:
            error_msg = utils.SERVER_CLIENT_NOT_IN_CHANNEL + '\n'
            socket.send(error_msg)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python server.py <port>" +
            "python server.py 12345")
        sys.exit(1)

    port = int(sys.argv[1])

    server_socket = MySocket("", port, channel_dict={}, client_dict={})
    server_socket.socket_list.append(server_socket)
    server_socket.bind()
    server_socket.listen(5)

    client_names = {}

    while 1:

        ready_to_read, ready_to_write, in_error = select.select(server_socket.socket_list, [], [], 0)

        for socket in ready_to_read:

            if socket == server_socket:

                new_socket, address = socket.accept()
                server_socket.socket_list.append(new_socket)
                name = new_socket.recv(utils.MESSAGE_LENGTH)
                client_names[new_socket] = name.strip()

            else:

                string = socket.recv(utils.MESSAGE_LENGTH)
                if string:
                    
                    string = string.strip()
                    process_string(server_socket, socket, string)

                else:
                    
                    if socket in server_socket.client_dict:

                        client_name = server_socket.client_dict[socket][0]
                        old_client_channel = server_socket.client_dict[socket][1]
                        msg = utils.SERVER_CLIENT_LEFT_CHANNEL.format(client_name)
                        broadcast(server_socket, socket, msg)
                        server_socket.channel_dict[old_client_channel].remove(socket)
                        server_socket.client_dict.pop(socket)
                        server_socket.socket_list.remove(socket)
                        client_names.pop(socket)    
                    # print(server_socket.channel_dict)
                    # print(server_socket.client_dict)
    server_socket.close()
