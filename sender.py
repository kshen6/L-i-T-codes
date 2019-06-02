from __future__ import division
"""
sender.py

To create a sender, run
    python sender.py [-proto]
where -proto can be -tcp or -udp.

Note also that we define NOISE as an intializing variable for the Sender class
We replicate noise in the chanel then as just the probability that the Sender
sends a packet or not
"""
import socket # for socket
import sys # for command line arguments
import random # for calculation of if to send packet
import time # for wait
import pickle

from lt import Encoder
from soliton import robust_soliton

class Sender():
    """
    Sender class, meant to represent the sender end of communication
    Sender.run is built to be run by a subprocess

    self.noise refers to the probability that sender does not send a packet
    """
    def __init__(self, blk_sz=20, soliton=robust_soliton, data=None, M=485, d=2, noise = 0.0):
        self.encoder = Encoder()
        if data is None:
            data = ''.join([str(random.randint(0, 1)) for _ in range(1000 * blk_sz)])
        self.encoder.create_blocks(data, blk_sz)
        self.message_generator = self.encoder.encode(0, soliton, M=M, d=d)
        # local host IP address to send to, we are sending a message to ourself
        self.ip = "127.0.0.1"
        # port to send message to
        self.port = 5008
        # constants that define what protocol to use
        self.protos = [socket.SOCK_DGRAM, socket.SOCK_STREAM]
        self.noise = noise

    def getMessage(self):
        """
        returns a message to be send to the receiever
        """
        s = next(self.message_generator)
        return pickle.dumps(s)

    def runUDP(self, sock):
        """
        runs UDP protocol on socket sock
        with probability noise, do not send packet
        """
        # just send entire message without check for completeness
        while True:
            # send message to receiver at IP, PORT
            if (self.noise < random.random()): sock.sendto(self.getMessage(), (self.ip, self.port))
            time.sleep(1)

    def runTCP(self, sock):
        """
        runs UDP protocol on socket sock
        """
        # connect to receiever, tls handshake
        sock.connect((self.ip, self.port))
        # continue to send massage until...
        while True:
            if (self.noise < random.random()): sock.sendall(self.getMessage())
            # data = sock.recv(1024)
            # print('Received', repr(data))
            # dont run line 73
            # print 'sending message: ' + str(pickle.loads(self.getMessage()))
            time.sleep(2)

    def run(self, proto):
        """
        runs sender, using the protocol described by the index proto
        """
        print 'targeting IP:', self.ip, 'target port:', self.port
        # print 'message:', self.getMessage()
        # open socket as sock
        sock = socket.socket(socket.AF_INET, self.protos[proto])
        if   proto == 0: self.runUDP(sock)
        elif proto == 1: self.runTCP(sock)


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
    else:
        print('specify the protocol you want to implement as:\n \
             python sender.py [-udp / -tcp ]')

if __name__ == '__main__':
    """
    create sender and run it
    """
    s = Sender()
    s.run(parseArgs())
