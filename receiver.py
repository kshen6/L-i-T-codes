"""
receiver.py

To create a receiver, run
    python receiver.py [-proto]
where -proto can be -tcp or -udp.
"""
import socket # for socket
import sys # for command line arguments

# local host IP address listen on
IP = "127.0.0.1"
# port we are listening on
PORT = 5005
# constants that define what protocol to use
PROTOS = [socket.SOCK_DGRAM, socket.SOCK_STREAM]

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
    # create socket to listen on
    sock = socket.socket(socket.AF_INET, # Internet
                         PROTOS[parseArgs()]) # UDP
    # bind socket to our IP and PORT
    sock.bind((IP, PORT))

    # continurally listen and print out message
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print('received message:', data.decode(), 'from ip: ', addr[0], ', port:', addr[1])
