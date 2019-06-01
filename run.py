from multiprocessing import Process, Pipe
import time
import random
from lt import Packet, Encoder, Decoder

# class NoisyPipe():
#     """
#     represents tunable noise in a a noisy channel.
#     This process sits between a sender and receiver
#     probabalistically dropping packets
#
#     piping works as:
#     external_pipe1 --- internal_pipe1 -- NOISE -- internal_pipe2 -- external_pipe2
#     """
#     def __init__(self, noise: float):
#         self.internal_pipes, self.external_pipes = [None] * 2, [None] * 2
#         self.internal_pipes[0], self.external_pipes[0] = Pipe()
#         self.internal_pipes[1], self.external_pipes[1] = Pipe()
#         self.noise = noise
#
#     def changeNoise(self, new_noise: float):
#         self.noise = new_noise
#
#     def getPipeEnd(self, index: int):
#         return self.external_pipes[index]
#
#     def send(self):
#         packet = self.internal_pipes[0].recv()
#         sefl.internal_piprs[1].send(packet)

class NoisyConnection():
    """
    Defines a connection with a tunable noise factor which defines how likely
    we are to send a given package. A package is lost with probability noise

    Based off of the Connection class defined in multiprocessing
    """
    def __init__(self, connection, noise: float):
        self.connection = connection
        self.noise = noise

    def changeNoise(self, new_noise: float):
        self.noise = new_noise

    def send(self, package):
        if (random.random() > self.noise):
            self.connection.send(package)

    def recv(self):
        return self.connection.recv()

    def close(self):
        close(self.connection)


class Sender():
    """
    Sender class, meant to represent the sender end of communication
    Sender.run is built to be run by a subprocess
    """
    def __init__(self):
        self.message = "hi there fren"

    # program run by sender process
    def run(self, noisyConn):
        while True:
            print('I\'m sending: ', self.message, ' to my friend')
            noisyConn.send(self.message)
            time.sleep(2)


class Receiver():
    """
    Sender class, meant to represent the sender end of communication
    Sender.run is built to be run by a subprocess
    """
    def __init__(self):
        pass

    # program run by receiver process
    def run(self, noisyConn):
        while True:
            mes = noisyConn.recv()
            print('ooh, I got a letter! It says: ', mes)


if __name__ == '__main__':
    # Define thta 30% of packages get lost
    NOISE = 0.3

    # build sender and receiver
    receiver, sender, = Receiver(), Sender()
    # build noiseless connections
    receiverConn, senderConn = Pipe() # from import multiprocessing

    pr = Process(target=receiver.run, args=(NoisyConnection(receiverConn, NOISE),)) # spawn receiver process
    ps = Process(target=sender.run, args=(NoisyConnection(senderConn, NOISE), )) # spawn sender process

    # begin processes
    pr.start()
    ps.start()
