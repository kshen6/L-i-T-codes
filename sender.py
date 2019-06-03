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
import mutex

from lt import Encoder
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
    def __init__(self, protocol, filename, packet_size=20, data=None, noise=0.0):
        #### NETWORK SETUP ####
        # local host IP address to send to, we are sending a message to ourself
        self.recv_ip, self.send_ip = "127.0.0.1", "127.0.0.1"
        # port to send message to
        self.recv_port, self.send_port = 5005, 5006
        # constants that define what protocol to use
        self.protos = [socket.SOCK_DGRAM, socket.SOCK_STREAM, socket.SOCK_DGRAM]
        self.proto = protocol

        #### SETUP ENCODER ####
        self.build_blocks(filename, packet_size)
        self.encode_blocks(filename, packet_size)

        self.file = filename
        self.noise = noise
        self.packetsSent = 0

    def build_blocks(self, filename, packet_size):
        filesize = os.path.getsize('./resources_to_send/' + filename)
        f = open('./resources_to_send/' + filename, "r")
        num_block = int(math.ceil(filesize / packet_size))
        self.blocks = []

        # Read data by blocks
        for i in range(num_block):
            data = f.read(packet_size)
            if not data:
                raise 'Stop.'
            # The last read bytes needs a right padding to be XORed in the future
            if len(data) != packet_size:
                data = data + '\0' * (packet_size - len(data)) # pad if necessary
                assert i == num_block - 1, 'Packet ' + str(i) + ' has a not handled size of ' + str(len(self.blocks[i])) + '  bytes.'
            # Packets are condensed in the right array type
            self.blocks.append(data)
        f.close()
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
                sock.sendto(pickle.dumps(block), (self.recv_ip, self.recv_port))
        sock.sendto(pickle.dumps(None), (self.recv_ip, self.recv_port))

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
        sock.connect((self.recv_ip, self.recv_port))
        # continue to send massage until...

        for block in self.blocks:
            self.packetsSent += 1
            if (self.noise < random.random()):
                # send message to receiver at IP, PORT
                print((block))
                # print(pickle.loads(pickle.dumps(block)))
                sock.sendall(pickle.dumps(block))
        for _ in range(10): # send constant number of sentinals
            sock.sendto(pickle.dumps(None), (self.recv_ip, self.recv_port))

    def listenForRecvToFinishThread(self):
        """
        thread function to wait for sentinal from receiver to say that they are done
        """
        sentinal_sock = socket.socket(socket.AF_INET, self.protos[self.proto])
        # bind socket to our IP and PORT
        sentinal_sock.bind((self.send_ip, self.send_port))
        while True:
            data, addr = sentinal_sock.recvfrom(64) # buffer size is 1024 bytes
            if not pickle.loads(data): # sentinal is None
                break
        self.recvFinshed = True
        sentinal_sock.close()

    def runLT(self, sock):
        """
        runs LT protocol on socket sock
        with probability noise, packet gets lost
        """
        # just send entire message without check for completeness
        self.recvFinshed = False
        sentinal_waiter = threading.Thread(target=self.listenForRecvToFinishThread)
        sentinal_waiter.setDaemon(True)
        sentinal_waiter.start()
        while (not self.recvFinshed):
            # send message to receiver at IP, PORT
            if (self.noise < random.random()):
                self.packetsSent += 1
                # send message to receiver at IP, PORT
                sock.sendto(pickle.dumps(next(self.message_generator)), (self.recv_ip, self.recv_port))
        sock.close()
        sentinal_waiter.join()

    def outputStats(self):
        """
        Outputs statistics
        """
        print 'Sender: sent {} total packet'.format(self.packetsSent)

    def run(self):
        """
        runs sender, using the protocol described by the index proto
        """
        print 'Sender: Targeting IP:', self.recv_ip, 'target port:', self.recv_port
        print 'Sender: sending ', self.file
        # print 'message:', self.getMessage()
        # open socket as sock
        sock = socket.socket(socket.AF_INET, self.protos[self.proto])
        if   self.proto == 0: self.runUDP(sock)
        elif self.proto == 1: self.runTCP(sock)
        elif self.proto == 2: self.runLT(sock)

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
    """
    create sender and run it
    """
    s = Sender(parseArgs(), 'Green_Eggs_and_Ham.txt', noise=0.00)
    s.run()
