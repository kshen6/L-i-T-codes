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
        self.port = 5005
        # constants that define what protocol to use
        self.protos = [socket.SOCK_DGRAM, socket.SOCK_STREAM]

    def getMessage(self):
        """
        returns a message to be send to the receiever
        """
        return self.message

    def run(self, proto: int):
        """
        runs sender, using the protocol described by the index proto
        """
        print('targeting IP:', self.ip, 'target port:', self.port)
        print('message:', self.getMessage())
        proto = parseArgs()
        while True:
            sock = socket.socket(socket.AF_INET, # Internet
                                 self.protos[proto]) # Protocol
            # send message to receiver at IP, PORT
            sock.sendto(self.getMessage().encode(), (self.ip, self.port))
            time.sleep(1)

def parseArgs():
    """
    parse command line to find what protocol to use
    """
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
    s.run(parseArgs)
