import sys
import socket
import select
import utils


class MySocket(socket.socket):

    def __init__(self, host, port, name=None, channel=None, socket_list=[], channel_dict=None, client_dict=None):

        super(MySocket, self).__init__()
        self.name = name
        self.host = host
        self.port = port
        self.channel = channel
        self.socket_list = socket_list
        self.channel_dict = channel_dict
        self.client_dict = client_dict

    def bind(self):
        
        super(MySocket, self).bind( (self.host, self.port) )

    def connect(self):
        super(MySocket, self).connect( (self.host, self.port) )

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_name(self):
        return self.name

    def get_channel(self):
        return self.channel

    def set_channel(self, channel):
        self.channel = channel


def pad_string(string):
    return string + ' ' * (200 - len(string))
    