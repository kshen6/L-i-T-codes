from __future__ import division
"""
receiver.py

To create a receiver, run
    python receiver.py [-proto]
where -proto can be -tcp or -udp.
"""
import socket # for socket
import sys # for command line arguments
from lt import Decoder
import pickle

class Receiver():
    """
    Sender class, meant to represent the sender end of communication
    Sender.run is built to be run by a subprocess
    """
    def __init__(self, proto, filename):
        #### NETWORK SETUP ####
        # local host ip of receiver and sender
        self.recv_ip, self.send_ip = "127.0.0.1", "127.0.0.1"
        # local port of receiver and sender
        self.recv_port, self.send_port = 5005, 5006
        # constants that define what protocol to use
        self.protos = [socket.SOCK_DGRAM, # UDP
                       socket.SOCK_STREAM, # TCP
                       socket.SOCK_DGRAM # LT
                       ]
        self.proto = proto

        #### DECODING SETUP ####
        self.packetsReceived = 0
        self.packets = []
        self.file = filename # file to write receive information to

    def runUDP(self, sock):
        """
        runs UDP protocol on socket sock
        """
        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            self.packetsReceived += 1
            data = pickle.loads(data)
            if not data: # sentinal received
                break
            self.packets.append(data)
        # no ordering or decoding to be done, just put packets into data
        self.data = [packet for packet in self.packets]

    def runTCP(self, sock):
        sock.listen(1)
        conn, addr = sock.accept()
        print 'Receiver: Connected to: {}'.format(addr)
        while True:
            data, addr = conn.recvfrom(1024) # buffer size is 1024 bytes
            self.packetsReceived += 1
            print(data)
            data_cpy = pickle.loads(data)
            if not data_cpy: # sentinal received
                break
            self.packets.append(data_cpy)
        self.data = [packet for packet in self.packets]

    def runLT(self, sock):
        """
        runs UDP protocol on socket sock
        """
        self.d = Decoder()
        while True:
            self.packetsReceived += 1
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            data = pickle.loads(data)
            # print 'Received message:', data, '   from ip:', addr[0], 'port:', addr[1]
            self.d.update_belief(data)
            if all(e is not None for e in self.d.belief):
                print 'Receiver: Completed decoding'
                break
        sock.sendto(pickle.dumps(None), (self.send_ip, self.send_port))
        sock.close()
        self.data = [data for data in self.d.belief]

    def writeData(self):
        """
        Write data received to a file defined by self.file
        Assumes that we have already decoded self.packets to self.data
        """
        f = open('./resources_received/' + self.file, "w+")
        for i in range(len(self.data) - 1):
            f.write(self.data[i])
        # get rid of padding on last block
        final_data = self.data[len(self.data) - 1]
        while final_data[-1] == '\0': final_data = final_data[:-1]
        f.write(final_data)
        print 'Receiver: received {}'.format(self.file)
        f.close()

    def outputStats(self):
        """
        Outputs statistics
        """
        print 'Receiver: received {} total packet'.format(self.packetsReceived)

    def run(self):
        """
        runs receiver, using the protocol described by the index proto
        """
        # create socket to listen on
        sock =  socket.socket(socket.AF_INET,
                           self.protos[self.proto])
        # bind socket to our IP and PORT
        sock.bind((self.recv_ip, self.recv_port))
        print "Receiver: Listening at ip {}, port {}".format(self.recv_ip, self.recv_port)
        if   self.proto == 0: self.runUDP(sock)
        elif self.proto == 1: self.runTCP(sock)
        elif self.proto == 2: self.runLT(sock)

        self.writeData()
        self.outputStats()


def parseArgs():
    """
    parse command line to find what protocol to use
    """
    if (len(sys.argv) < 2):
        print('specify the protocol you want to implement')
        exit(1)
    if   (sys.argv[1] == '-udp'): return 0
    elif (sys.argv[1] == '-tcp'): return 1
    elif (sys.argv[1] == '-lt' ): return 2
    else:
        print('specify the protocol you want to implement as:\n \
             python sender.py [-udp / -tcp ]')

if __name__ == '__main__':
    r = Receiver(parseArgs(), 'Green_Eggs_and_Ham.txt')
    r.run()
