"""
run.py

creates both a reciever and sender and then runs both in parallel

to run use:
    python run.py [-proto]
where -proto can be -tcp or -udp.
"""
# built in packages
from multiprocessing import Process # for multiprocessing
import time     # for sleep and timing
import sys      # for argument parsing
import random   # RNG
# our own packages
from lt import Packet, Encoder, Decoder
from receiver import Receiver, parseArgs
from sender import Sender

if __name__ == '__main__':
    # Define thta 30% of packages get lost
    NOISE = 0.3

    # build sender and receiver
    receiver, sender, = Receiver(), Sender()

    pr = Process(target=receiver.run, args=(parseArgs(),)) # spawn receiver process
    ps = Process(target=sender.run, args=(parseArgs(), )) # spawn sender process

    # begin processes
    pr.start()
    ps.start()
