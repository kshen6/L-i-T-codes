"""
receiver.py

To create a receiver, run
    python receiver.py [-proto]
where -proto can be -tcp or -udp.
"""
import socket # for socket
import sys # for command line arguments
import pickle
from rq import decode
class Receiver():
    """
    Sender class, meant to represent the sender end of communication
    Sender.run is built to be run by a subprocess
    """
    def __init__(self):
        # local host IP address listen on
        self.ip = "127.0.0.1"
        # port we are listening on
        self.port = 5008
        # constants that define what protocol to use
        self.protos = [socket.SOCK_DGRAM, socket.SOCK_STREAM]

    def runUDP(self, sock):
        """
        runs UDP protocol on socket sock
        """
        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            print'Received message:', decode(pickle.loads(data)), '   from ip:', addr[0], 'port:', addr[1]

    def runTCP(self, sock):
        sock.listen(1)
        conn, addr = sock.accept()
        print('Connected to:', addr)
        while True:
            data = conn.recvfrom(1024) # buffer size is 1024 bytes
            print 'received message:', data
            # if not data:
            #     break
            # conn.sendall(data)

    # program run by receiver process
    def run(self, proto):
        """
        runs receiver, using the protocol described by the index proto
        """
        # create socket to listen on
        sock =  socket.socket(socket.AF_INET,
                           self.protos[proto])
        # bind socket to our IP and PORT
        sock.bind((self.ip, self.port))
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
        print('supported protocols include: -udp, -tcp')
        exit(1)

if __name__ == '__main__':
    r = Receiver()
    r.run(parseArgs())
