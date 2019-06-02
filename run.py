"""
run.py

creates both a reciever and sender and then runs both in parallel

to run both a sender and a receiver that work in one terminal window do:
    python run.py [-proto]
where -proto can be -tcp or -udp.

you can also run:
    python sender.py [-proto]
    python receiver.py [-proto]
where -proto can be -tcp or -udp in two seperate terminal windows in order to
run each user seperately
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
    NOISE = 0.0

    # build sender and receiver
    receiver, sender, = Receiver(), Sender(noise = NOISE)

    pr = Process(target=receiver.run, args=(parseArgs(), )) # spawn receiver process
    ps = Process(target=sender.run, args=(parseArgs(), )) # spawn sender process

    # begin processes
    pr.start()
    ps.start()
