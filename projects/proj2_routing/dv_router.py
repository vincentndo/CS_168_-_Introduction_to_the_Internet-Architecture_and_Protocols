"""Your awesome Distance Vector router for CS 168."""

import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter(basics.DVRouterBase):
    # NO_LOG = True # Set to True on an instance to disable its logging
    # POISON_MODE = True # Can override POISON_MODE here
    # DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

    def __init__(self):
        """
        Called when the instance is initialized.

        You probably want to do some additional initialization here.

        """
        self.start_timer()  # Starts calling handle_timer() at correct rate
        self.routing_table = {}
        self.links = {}
        self.timer_dict = {}


    def _broadcast_table(self):
        for i in self.routing_table:
            port, latency = self.routing_table[i]
            packet = basics.RoutePacket(i, latency)
            self.send(packet, port=port, flood=True)


    def _poison_route(self, port_down):

        destinations_down = []
        for d in self.routing_table:
            if self.routing_table[d][0] == port_down:
                destinations_down.append(d)

        for d in destinations_down:
            packet = basics.RoutePacket(d, INFINITY)
            self.send(packet, port=port_down, flood=True)


    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        self.links[port] = latency
        self._broadcast_table()
        

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        if self.POISON_MODE:
            self._poison_route(port)

        self.links.pop(port)
        to_be_removed = []
        for d in self.routing_table:
            if self.routing_table[d][0] == port:
                to_be_removed.append(d)

        for d in to_be_removed:
            self.routing_table.pop(d)
            if d in self.timer_dict:
                self.timer_dict[d].cancel()
                self.timer_dict.pop(d)

        self._broadcast_table()


    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):

            latency, destination = packet.latency, packet.destination
            if latency == INFINITY:

                if destination in self.routing_table:
                    self.routing_table.pop(destination)
                    if destination in self.timer_dict:
                        self.timer_dict[destination].cancel()
                        self.timer_dict.pop(destination)
                else:
                    pass

            else:

                new_latency = latency + self.links[port]

                if destination not in self.routing_table:

                    self.routing_table[destination] = (port, new_latency)
                    args_list = [destination, None]
                    timer = api.create_timer(self.ROUTE_TIMEOUT, self.routing_table.pop, recurring=False, args=args_list)
                    self.timer_dict[destination] = timer

                else:

                    if (new_latency <= self.routing_table[destination][1]):

                        self.routing_table[destination] = (port, new_latency)
                        if destination in self.timer_dict:
                            self.timer_dict[destination].cancel()
                        args_list = [destination, None]
                        timer = api.create_timer(self.ROUTE_TIMEOUT, self.routing_table.pop, recurring=False, args=args_list)
                        self.timer_dict[destination] = timer

        elif isinstance(packet, basics.HostDiscoveryPacket):
            src = packet.src
            self.routing_table[src] = (port, self.links[port])

        else:
            # Totally wrong behavior for the sake of demonstration only: send
            # the packet back to where it came from!
            # self.send(packet, port=port)

            dst = packet.dst
            if dst in self.routing_table and port != self.routing_table[dst][0]:
                self.send(packet, port=self.routing_table[dst][0])


    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        self._broadcast_table()
