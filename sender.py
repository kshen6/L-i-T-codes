"""
sender.py

To create a sender, run
    python sender.py [-proto]
where -proto can be -tcp or -udp.

"""
import socket # for socket
import sys # for command line arguments

# local host IP address to send to, we are sending a message to ourself
IP = "127.0.0.1"
# port to send message to
PORT = 5005
# constants that define what protocol to use
PROTOS = [socket.SOCK_DGRAM, socket.SOCK_STREAM]

def createMessage():
    """
    returns a message to be send to the receiever
    """
    return "Hello World"

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
    print('targeting IP:', IP, 'target port:', PORT)
    print('message:', createMessage())
    proto = parseArgs()

    sock = socket.socket(socket.AF_INET, # Internet
                         PROTOS[proto]) # Protocol

    # send message to receiver at IP, PORT
    sock.sendto(createMessage().encode(), (IP, PORT))
