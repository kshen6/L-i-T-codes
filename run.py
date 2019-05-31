from multiprocessing import Process
import time
from lt import Packet, Encoder, Decoder

class NoisyPipe():
    """
    represents tunable noise in a a noisy channel.
    This process sits between a sender and receiver
    probabalistically dropping packets

    piping works as:
    external_pipe1 --- internal_pipe1 -- NOISE -- internal_pipe2 -- external_pipe2
    """
    def __init__(self, noise: float):
        self.internal_pipes, self.external_pipes = [None] * 2, [None] * 2
        self.internal_pipes[0], self.external_pipes[0] = Pipe()
        self.internal_pipes[1], self.external_pipes[1] = Pipe()
        self.noise = noise

    def changeNoise(self, new_noise: float):
        self.noise = new_noise

    def getPipeEnd(self, index: int):
        return self.external_pipes[index]

    def send(self):
        packet = self.internal_pipes[0].recv()
        sefl.internal_piprs[1].send(packet)

class Sender():
    """
    Sender class, meant to represent the sender end of communication
    Sender.run is built to be run by a subprocess
    """
    def __init__(self):
        self.message = "hi from sender"

    def run(self):
        while True:
            print(self.message)
            time.sleep(2)


class Receiver():
    """
    Sender class, meant to represent the sender end of communication
    Sender.run is built to be run by a subprocess
    """
    def __init__(self):
        self.message = "hi from receiver"

    def run(self):
        while True:
            print(self.message)
            time.sleep(2)


if __name__ == '__main__':
    r = Receiver()
    s = Sender()
    pr = Process(target=r.run) # receiver process
    ps = Process(target=s.run) # sender process
    pr.start()
    ps.start()
