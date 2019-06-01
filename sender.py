"""
sender.py

To create a sender, run
    python sender.py [-proto]
where -proto can be -tcp or -udp.

"""
import socket # for socket
import sys # for command line arguments
import time # for wait

class Sender():
    """
    Sender class, meant to represent the sender end of communication
    Sender.run is built to be run by a subprocess
    """
    def __init__(self):
        self.message = "hi there fren"
        # local host IP address to send to, we are sending a message to ourself
        self.ip = "127.0.0.1"
        # port to send message to
        self.port = 5008
        # constants that define what protocol to use
        self.protos = [socket.SOCK_DGRAM, socket.SOCK_STREAM]

    def getMessage(self):
        """
        returns a message to be send to the receiever
        """
        return self.message

    def runUDP(self, sock):
        """
        runs UDP protocol on socket sock
        """
        # just send entire message without check for completeness
        while True:
            # send message to receiver at IP, PORT
            sock.sendto(self.getMessage().encode(), (self.ip, self.port))
            time.sleep(1)

    def runTCP(self, sock):
        """
        runs UDP protocol on socket sock
        """
        # connect to receiever, tls handshake
        sock.connect((self.ip, self.port))
        # continue to send massage until...
        while True:
            sock.sendall(self.getMessage().encode())
            # data = sock.recv(1024)
            # print('Received', repr(data))
            print('sending: ', self.getMessage())
            time.sleep(2)

    def run(self, proto: int):
        """
        runs sender, using the protocol described by the index proto
        """
        print('targeting IP:', self.ip, 'target port:', self.port)
        print('message:', self.getMessage())
        # open socket as sock
        with socket.socket(socket.AF_INET, self.protos[proto]) as sock:
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
