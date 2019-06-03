from __future__ import division
"""
sender.py
To create a sender, run
    python sender.py [-proto]
where -proto can be -tcp or -udp or -lt.
Note also that we define NOISE as an intializing variable for the Sender class
We replicate noise in the chanel then as just the probability that the Sender
sends a packet or not
"""
import socket # for socket
import sys # for command line arguments
import random # for calculation of if to send packet
import time # for wait
import pickle
import numpy as np
import math
import os # for file read and write
import threading

from lt import Encoder
from rq import encode
from soliton import robust_soliton

class TCPPacket():
    """
    Defines a packet for a TCP connection
    """
    def __init__(self, data, numPackets, index):
        self.data = data
        self.numPackets = numPackets
        self.index = index

class Sender():
    """
    Sender class, meant to represent the sender end of communication
    Sender.run is built to be run by a subprocess
    self.noise refers to the probability that sender does not send a packet
    """
    def __init__(self, protocol, file, packet_size=20, data=None, noise=0.0):
        #### NETWORK SETUP ####
        # local host IP address to send to, we are sending a message to ourself
        self.ip = "127.0.0.1"
        # port to send message to
        self.port = 5005
        # constants that define what protocol to use
        self.protos = [socket.SOCK_DGRAM, socket.SOCK_STREAM, socket.SOCK_DGRAM]
        self.proto = protocol

        #### SETUP ENCODER ####
        self.build_blocks(file, packet_size)
        self.encode_blocks(file, packet_size)

        self.file = file
        self.noise = noise
        self.packetsSent = 0

        # for RaptorQ
        self.max_memory = 2000
        # self.encoded_data = encode([], self.message)
        # self.data_len, self.oti_scheme, self.oti_common, self.symbols = self.encoded_data

    def build_blocks(self, file, packet_size):
        """
        Read the given file by blocks of `core.PACKET_SIZE` and use np.frombuffer() improvement.
        By default, we store each octet into a np.uint8 array space, but it is also possible
        to store up to 8 octets together in a np.uint64 array space.
        This process is not saving memory but it helps reduce dimensionnality, especially for the
        XOR operation in the encoding. Example:
        * np.frombuffer(b'x01x02', dtype=np.uint8) => array([1, 2], dtype=uint8)
        * np.frombuffer(b'x01x02', dtype=np.uint16) => array([513], dtype=uint16)
        """
        filesize = os.path.getsize('./resources_to_send/' + file)
        f = open('./resources_to_send/' + file, "r")
        num_block = int(math.ceil(filesize / packet_size))
        self.blocks = []
        
        # if not RaptorQ
        if self.proto != 3: 
            # Read data by blocks of size core.PACKET_SIZE
            for i in range(num_block):
                data = f.read(packet_size)
                if not data:
                    raise 'Stop.'
                # The last read bytes needs a right padding to be XORed in the future
                if len(data) != packet_size:
                    data = data + ' ' * (packet_size - len(data)) # pad if necessary
                    assert i == num_block - 1, 'Packet ' + str(i) + ' has a not handled size of ' + str(len(self.blocks[i])) + '  bytes.'
                # Packets are condensed in the right array type
                self.blocks.append(data)
        else:
            data = open(self.file, 'r').read()
            self.blocks = encode([packet_size, packet_size, self.max_memory], data)
        # print "data ============== \n"
        print 'Sender: num blocks: ' + str(len(self.blocks))
        # self.message_generator = iter(self.blocks)

    def encode_blocks(self, file, packet_size, M=485, d=2):
        """
        Encode blocks into packets to be sent over channel
        """
        if self.proto == 0: # UDP
            # no need to do any encoding for UDP
            self.packets = [packet for packet in self.blocks]
        if self.proto == 1: # TCP
            self.sentPacket = [False for _ in range(len(self.blocks))]
            self.packets = [packet for packet in self.blocks]
        if self.proto == 2: # LT
            self.encoder = Encoder()
            self.encoder.create_blocks(self.blocks)
            self.message_generator = self.encoder.encode(0, robust_soliton, M=M, d=d)
        if self.proto == 3: #RQ
            # blocks should already have been encoded in build_blocks
            # self.blocks is in tuple format: (self.data_len, self.oti_scheme, self.oti_common, self.symbols)
            self.data_len, self.oti_scheme, self.oti_common, self.packets = self.blocks

    def runUDP(self, sock):
        """
        runs UDP protocol on socket sock
        with probability noise, packet gets lost
        """
        # just send entire message without check for completeness
        for block in self.blocks:
            self.packetsSent += 1
            if (self.noise < random.random()):
                # send message to receiver at IP, PORT
                sock.sendto(pickle.dumps(block), (self.ip, self.port))
        for _ in range(10): # send constant number of sentinals
            sock.sendto(pickle.dumps(None), (self.ip, self.port))

    def receiveTCP(self):
        pass

    def sendTCP(self):
        pass

    def runTCP(self, sock):
        """
        runs TCP protocol on socket sock
        WILL PROBABLY HAVE TO IMPLEMENT TCP MYSELF
        TODO
        USING THREADING IN ORDER TO KEEP TRACK OF WHAT HAS BEEN SENT ALREADY
        """
        # connect to receiever, tls handshake
        sock.connect((self.ip, self.port))
        # continue to send massage until...

        for block in self.blocks:
            self.packetsSent += 1
            if (self.noise < random.random()):
                # send message to receiver at IP, PORT
                print((block))
                # print(pickle.loads(pickle.dumps(block)))
                sock.sendall(pickle.dumps(block))
        for _ in range(10): # send constant number of sentinals
            sock.sendto(pickle.dumps(None), (self.ip, self.port))

    def runLT(self, sock):
        """
        runs LT protocol on socket sock
        with probability noise, packet gets lost
        """
        # just send entire message without check for completeness
        for _ in range(50 * len(self.blocks)):
            # send message to receiver at IP, PORT
            self.packetsSent += 1
            if (self.noise < random.random()):
                # send message to receiver at IP, PORT
                sock.sendto(pickle.dumps(next(self.message_generator)), (self.ip, self.port))
    
    def runRQ(self, sock):
        """
        runs RaptorQ protocol on socket sock
        with probability noise, packet gets lost
        """

        for _ in range(50 * len(self.blocks)):
            # send message to receiver at IP, PORT
            self.packetsSent += 1

            if (self.noise < random.random()):
                # choose random symbol to send
                next_block_key, next_block_val = random.choice(list(self.packets.items()))
                message = (self.data_len, self.oti_scheme, self.oti_common, (next_block_key, next_block_val))

                # send message to receiver at IP, PORT
                sock.sendto(pickle.dumps(message), (self.ip, self.port))

    def outputStats(self):
        """
        Outputs statistics
        """
        print 'Sender: sent {} total packet'.format(self.packetsSent)

    def run(self):
        """
        runs sender, using the protocol described by the index proto
        """
        print 'Sender: Targeting IP:', self.ip, 'target port:', self.port
        print 'Sender: sending ', self.file
        # print 'message:', self.getMessage()
        # open socket as sock
        sock = socket.socket(socket.AF_INET, self.protos[self.proto])
        if   self.proto == 0: self.runUDP(sock)
        elif self.proto == 1: self.runTCP(sock)
        elif self.proto == 2: self.runLT(sock)
        elif self.proto == 3: self.runRQ(sock)

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
    elif (sys.argv[1] == '-rq'):
        return 3
    else:
        print('specify the protocol you want to implement as:\n \
             python sender.py [-udp / -tcp / -rq]')

if __name__ == '__main__':
    """
    create sender and run it
    """
    s = Sender(parseArgs(), 'Green_Eggs_and_Ham.txt', noise=0.00)
    s.run()

# """
# sender.py

# To create a sender, run
#     python sender.py [-proto]
# where -proto can be -tcp or -udp.

# Note also that we define NOISE as an intializing variable for the Sender class
# We replicate noise in the chanel then as just the probability that the Sender
# sends a packet or not
# """
# import socket # for socket
# import sys # for command line arguments
# import random # for calculation of if to send packet
# import time # for wait
# import pickle
# import random
# from rq import encode


# class Sender():
#     """
#     Sender class, meant to represent the sender end of communication
#     Sender.run is built to be run by a subprocess

#     self.noise refers to the probability that sender does not send a packet
#     """
#     def __init__(self, noise = 0.0):
#         self.file = open('Harry_Pottter_and_the_Sorcerer.txt', 'r')
#         self.message = self.file.read()
#         self.encoded_data = encode([], self.message)
#         self.data_len, self.oti_scheme, self.oti_common, self.symbols = self.encoded_data
#         # local host IP address to send to, we are sending a message to ourself
#         self.ip = "127.0.0.1"
#         # port to send message to
#         self.port = 5008
#         # constants that define what protocol to use
#         self.protos = [socket.SOCK_DGRAM, socket.SOCK_STREAM]
#         self.noise = noise
#         self.curr_data = dict()

#     def getMessage(self):
#         """
#         returns a message to be sent to the receiver
#         """

#         # data_len, oti_scheme, oti_common, symbols = data
#         next_block_key, next_block_val = random.choice(list(self.symbols.items()))
#         # self.curr_data[next_block_key] = next_block_val
#         return (self.data_len, self.oti_scheme, self.oti_common, (next_block_key, next_block_val))

#     def runUDP(self, sock):
#         """
#         runs UDP protocol on socket sock
#         with probability noise, do not send packet
#         """
#         numPackets = 0
#         # just send entire message without check for completeness
#         while True:
#             # send message to receiver at IP, PORT
#             numPackets += 1
#             if (self.noise < random.random()): sock.sendto(pickle.dumps(self.getMessage()), (self.ip, self.port))
#             # time.sleep(1)
#         print 'numPackets sent: ', numPackets

#     def runTCP(self, sock):
#         """
#         runs UDP protocol on socket sock
#         """
#         # connect to receiever, tls handshake
#         sock.connect((self.ip, self.port))
#         # continue to send message until...
#         while True:
#             if (self.noise < random.random()): sock.sendall(pickle.dumps(self.getMessage()))
#             # data = sock.recv(1024)
#             # print('Received', repr(data))
#             print('sending: ', self.getMessage())
#             time.sleep(2)

#     def run(self, proto):
#         """
#         runs sender, using the protocol described by the index proto
#         """
#         print 'targeting IP:', self.ip, 'target port:', self.port
#         print 'message:', self.getMessage()
#         # open socket as sock
#         sock = socket.socket(socket.AF_INET, self.protos[proto])
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
#         print('specify the protocol you want to implement as:\n \
#              python sender.py [-udp / -tcp ]')

# if __name__ == '__main__':
#     """
#     create sender and run it
#     """
#     s = Sender()
#     s.run(parseArgs())
