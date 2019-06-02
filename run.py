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
# from multiprocessing import Process # for multiprocessing
import os
import time     # for sleep and timing
import sys      # for argument parsing
import random   # RNG
import filecmp # to compare outputs from sender and receiver
# our own packages
from lt import Packet, Encoder, Decoder
from receiver import Receiver, parseArgs
from sender import Sender

if __name__ == '__main__':
    # Defined constants to test
    NOISE = 0.4
    file = 'Harry_Pottter_and_the_Sorcerer.txt'
    # file = 'stanford.png'
    # file = 'Green_Eggs_and_Ham.txt'

    # spawn receiver
    recv_pid = os.fork()
    if recv_pid == 0:
        receiver = Receiver(parseArgs(), file)
        receiver.run()
        exit(0)
    # spawn sender
    send_pid = os.fork()
    if send_pid == 0:
        sender = Sender(parseArgs(), file, noise=NOISE, packet_size = 50)
        sender.run()
        exit(0)

    # wait for sender and receiver to be finished
    os.waitpid(send_pid, 0)
    os.waitpid(recv_pid, 0)

    # output results
    print('Both Sender and Receiver have exited')
    if filecmp.cmp('./resources_to_send/' + file, './resources_received/' + file):
        print('Sent and received files match!')
    else:
        print('Sent and received files differ')
