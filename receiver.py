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
from rq import RaptorDecoder
import pickle

class Receiver():
    """
    Sender class, meant to represent the sender end of communication
    Sender.run is built to be run by a subprocess
    """
    def __init__(self, proto, file):
        #### NETWORK SETUP ####
        # local host IP address listen on
        self.ip = "127.0.0.1"
        # port we are listening on
        self.port = 5005
        # constants that define what protocol to use
        self.protos = [socket.SOCK_DGRAM, # UDP
                       socket.SOCK_STREAM, # TCP
                       socket.SOCK_DGRAM # LT
                       ]
        self.proto = proto

        #### DECODING SETUP ####
        self.packetsReceived = 0
        self.packets = []
        self.file = file # file to write receive information to

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
            data = pickle.loads(data)
            if not data: # sentinal received
                break
            self.packets.append(data)
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
                print 'Completed decoding'
                break
        self.data = [data for data in self.d.belief]

    def runRQ(self, sock):
        """
        runs UDP protocol on socket sock with Raptor decoding
        """
        self.d = RaptorDecoder()
        while True:
            self.packetsReceived += 1
            data, addr = sock.recvfrom(10000) # buffer size is 1024 bytes
            loaded_data = pickle.loads(data)
            self.d.symbols[loaded_data[3][0]]=loaded_data[3][1]
            message = 'Not enough data yet...'
            if self.packetsReceived %100 == 0:
                message = self.d.decode(pickle.loads(data))
            if message != 'Not enough data yet...': break
            # print'Received message:', self.d.decode(pickle.loads(data)), '   from ip:', addr[0], 'port:', addr[1]
        
        print'Received message:', message, '   from ip:', addr[0], 'port:', addr[1]
        # print 'numPackets received: ', self.packetsReceived



    def writeData(self):
        """
        Write data received to a file defined by self.file
        Assumes that we have already decoded self.packets to self.data
        """
        f = open('./resources_received/' + self.file, "w")
        for data in self.data:
            f.write(data)
        print 'Receiver: received {}'.format(self.file)

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
        sock.bind((self.ip, self.port))
        print "Receiver: Listening at ip {}, port {}".format(self.ip, self.port)
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
    if (sys.argv[1] == '-udp'):
        return 0
    elif (sys.argv[1] == '-tcp'):
        return 1
    elif (sys.argv[1] == '-lt'):
        return 2
    else:
        print('specify the protocol you want to implement as:\n \
             python sender.py [-udp / -tcp ]')

if __name__ == '__main__':
    r = Receiver(parseArgs(), 'Green_Eggs_and_Ham.txt')
    r.run()
# """
# receiver.py

# To create a receiver, run
#     python receiver.py [-proto]
# where -proto can be -tcp or -udp.
# """
# import socket # for socket
# import sys # for command line arguments
# import pickle
# from rq import Decoder

# class Receiver():
#     """
#     Sender class, meant to represent the sender end of communication
#     Sender.run is built to be run by a subprocess
#     """
#     def __init__(self):
#         # local host IP address listen on
#         self.ip = "127.0.0.1"
#         # port we are listening on
#         self.port = 5008
#         # constants that define what protocol to use
#         self.protos = [socket.SOCK_DGRAM, socket.SOCK_STREAM]

#     def runUDP(self, sock):
#         """
#         runs UDP protocol on socket sock
#         """
#         self.d = Decoder()
#         numPackets = 0
#         message = ''
#         while True:
#             numPackets += 1
#             data, addr = sock.recvfrom(10000) # buffer size is 1024 bytes
#             loaded_data = pickle.loads(data)
#             self.d.symbols[loaded_data[3][0]]=loaded_data[3][1]
#             message = 'Not enough data yet...'
#             if numPackets %100 == 0:
#                 message = self.d.decode(pickle.loads(data))
#             if message != 'Not enough data yet...': break
#             # print'Received message:', self.d.decode(pickle.loads(data)), '   from ip:', addr[0], 'port:', addr[1]
#         print'Received message:', message, '   from ip:', addr[0], 'port:', addr[1]
#         print 'numPackets received: ', numPackets

#     def runTCP(self, sock):
#         sock.listen(1)
#         conn, addr = sock.accept()
#         print('Connected to:', addr)
#         while True:
#             data = conn.recvfrom(1024) # buffer size is 1024 bytes
#             print 'received message:', data
#             # if not data:
#             #     break
#             # conn.sendall(data)

#     # program run by receiver process
#     def run(self, proto):
#         """
#         runs receiver, using the protocol described by the index proto
#         """
#         # create socket to listen on
#         sock =  socket.socket(socket.AF_INET,
#                            self.protos[proto])
#         # bind socket to our IP and PORT
#         sock.bind((self.ip, self.port))
#         if   proto == 0: self.runUDP(sock)
#         elif proto == 1: self.runTCP(sock)


# def parseArgs():
#     """
#     parse command line to find what protocol to use
#     """
#     if (len(sys.argv) < 2):
#         print('specify the protocol you want to implement')
#         exit(1)
#     if (sys.argv[1] == '-udp'):
#         return 0
#     elif (sys.argv[1] == '-tcp'):
#         return 1
#     else:
#         print('supported protocols include: -udp, -tcp')
#         exit(1)

# if __name__ == '__main__':
#     r = Receiver()
#     r.run(parseArgs())
