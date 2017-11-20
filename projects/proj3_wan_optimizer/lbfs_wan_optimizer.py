import wan_optimizer
from tcp_packet import Packet
from utils import *


class WanOptimizer(wan_optimizer.BaseWanOptimizer):
    """ WAN Optimizer that divides data into variable-sized
    blocks based on the contents of the file.

    This WAN optimizer should implement part 2 of project 4.
    """

    # The string of bits to compare the lower order 13 bits of hash to
    GLOBAL_MATCH_BITSTRING = '0111011001010'

    def __init__(self):
        wan_optimizer.BaseWanOptimizer.__init__(self)
        # Add any code that you like here (but do not add any constructor arguments).
        self.cache = {}
        self.buffer = {}
        return


    def _send_helper(self, src, dest, is_fin, payload, to_address):

        if (not len(payload)) and is_fin:
            fin_packet = Packet(src, dest, True, is_fin, '')
            self.send(fin_packet, to_address)
            return

        key = get_hash(payload)
        if key in self.cache:
            if to_address == self.wan_port:
                hash_packet = Packet(src, dest, False, is_fin, key)
                self.send(hash_packet, to_address)
                return
            text = self.cache[key]
        else:
            self.cache[key] = payload
            text = payload

        n = len(text) / MAX_PACKET_SIZE
        subtext_list = [ text[i:min(len(text), i + MAX_PACKET_SIZE)] for i in range(0, len(text), MAX_PACKET_SIZE) ]

        for i in range(len(subtext_list) - 1):
            packet = Packet(src, dest, True, False, subtext_list[i])
            self.send(packet, to_address)
        packet = Packet(src, dest, True, is_fin, subtext_list[-1])
        self.send(packet, to_address)


    def _process_packets(self, packet, to_address):
        src, dest = packet.src, packet.dest
        remaining_size = min( (len(self.buffer[(src, dest)]) - packet.size()), 47)
        start_point = len(self.buffer[(src, dest)]) - packet.size() - remaining_size
        data = self.buffer[(src, dest)][start_point:]
        
        cutoff_points = []
        if len(data) >= 48:
            for i in range(len(data) - 47):
                hash_data = get_hash(data[i:i+48])
                last_13_bits = get_last_n_bits(hash_data, 13)
                if last_13_bits == WanOptimizer.GLOBAL_MATCH_BITSTRING:
                    cutoff_points.append(start_point + i + 48)

        i = 0
        for j in cutoff_points:
            data_block = self.buffer[(src, dest)][i:j]
            i = j
            self._send_helper(src, dest, False, data_block, to_address)
        self.buffer[(src, dest)] = self.buffer[(src, dest)][i:]

        if packet.is_fin:
            data_block = self.buffer[(src, dest)]
            self._send_helper(src, dest, packet.is_fin, data_block, to_address)
            self.buffer.pop((src, dest))


    def receive(self, packet):
        """ Handles receiving a packet.

        Right now, this function simply forwards packets to clients (if a packet
        is destined to one of the directly connected clients), or otherwise sends
        packets across the WAN. You should change this function to implement the
        functionality described in part 2.  You are welcome to implement private
        helper fuctions that you call here. You should *not* be calling any functions
        or directly accessing any variables in the other middlebox on the other side of 
        the WAN; this WAN optimizer should operate based only on its own local state
        and packets that have been received.
        """
        if packet.dest in self.address_to_port:
            # The packet is destined to one of the clients connected to this middlebox;
            # send the packet there.
            src, dest = packet.src, packet.dest
            if packet.is_raw_data:
                if (src, dest) not in self.buffer:
                    self.buffer[(src, dest)] = packet.payload
                else:
                    self.buffer[(src, dest)] += packet.payload

                self._process_packets(packet, self.address_to_port[packet.dest])
            else:
                text = self.cache[packet.payload]
                self._send_helper(src, dest, packet.is_fin, text, self.address_to_port[packet.dest])

        else:
            # The packet must be destined to a host connected to the other middlebox
            # so send it across the WAN.
            src, dest = packet.src, packet.dest
            if (src, dest) not in self.buffer:
                self.buffer[(src, dest)] = packet.payload
            else:
                self.buffer[(src, dest)] += packet.payload

            self._process_packets(packet, self.wan_port)
