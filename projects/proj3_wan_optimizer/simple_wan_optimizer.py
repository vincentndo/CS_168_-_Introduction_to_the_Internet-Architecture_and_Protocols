import wan_optimizer
from tcp_packet import Packet
from utils import *


class WanOptimizer(wan_optimizer.BaseWanOptimizer):
    """ WAN Optimizer that divides data into fixed-size blocks.

    This WAN optimizer should implement part 1 of project 4.
    """

    # Size of blocks to store, and send only the hash when the block has been
    # sent previously
    BLOCK_SIZE = 8000

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
        packets_size = sum( [p.size() for p in self.buffer[(src, dest)]] )

        if packets_size <= WanOptimizer.BLOCK_SIZE:
            text = ''.join( [p.payload for p in self.buffer[(src, dest)]] )

            if packet.is_fin:
                self._send_helper(src, dest, True, text, to_address)
                self.buffer.pop((src, dest))
            elif packets_size == WanOptimizer.BLOCK_SIZE:
                self._send_helper(src, dest, False, text, to_address)
                self.buffer[(src, dest)] = []

        else:
            last_packet = self.buffer[(src, dest)].pop(-1)
            leftover_size = packets_size - WanOptimizer.BLOCK_SIZE
            cutoff_point = last_packet.size() - leftover_size
            text = ''.join([p.payload for p in self.buffer[(src, dest)]])
            text += last_packet.payload[:cutoff_point]
            self._send_helper(src, dest, False, text, to_address)

            if packet.is_fin:
                self._send_helper(src, dest, True, last_packet.payload[cutoff_point:], to_address)
                self.buffer.pop((src, dest))
            else:
                leftover_packet = Packet(src, dest, True, False, last_packet.payload[cutoff_point:])
                self.buffer[(src, dest)] = [leftover_packet]


    def receive(self, packet):
        """ Handles receiving a packet.

        Right now, this function simply forwards packets to clients (if a packet
        is destined to one of the directly connected clients), or otherwise sends
        packets across the WAN. You should change this function to implement the
        functionality described in part 1.  You are welcome to implement private
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
                    self.buffer[(src, dest)] = [packet]
                else:
                    self.buffer[(src, dest)].append(packet)

                self._process_packets(packet, self.address_to_port[packet.dest])
            else:
                text = self.cache[packet.payload]
                self._send_helper(src, dest, packet.is_fin, text, self.address_to_port[packet.dest])

        else:
            # The packet must be destined to a host connected to the other middlebox
            # so send it across the WAN.
            src, dest = packet.src, packet.dest
            if (src, dest) not in self.buffer:
                self.buffer[(src, dest)] = [packet]
            else:
                self.buffer[(src, dest)].append(packet)
            self._process_packets(packet, self.wan_port)
