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


def run(FILENAME, NOISE, PACK_SIZE, numReceived, numSent, matches):
    # spawn receiver
    recv_pid = os.fork()
    if recv_pid == 0:
        receiver = Receiver(parseArgs(), FILENAME)
        receiver.run()
        numReceived.write('{}\n'.format(receiver.packetsReceived))
        exit(0)
    # spawn sender
    send_pid = os.fork()
    if send_pid == 0:
        sender = Sender(parseArgs(), FILENAME, noise=NOISE, packet_size = PACK_SIZE)
        sender.run()
        numSent.write('{}\n'.format(sender.packetsSent))
        exit(0)

    # wait for sender and receiver to be finished
    os.waitpid(send_pid, 0)
    os.waitpid(recv_pid, 0)

    if filecmp.cmp('./resources_to_send/' + FILENAME, './resources_received/' + FILENAME):
        matches.append(1)

if __name__ == '__main__':
    ans = []
    NOISE = 0
    STEP_SIZE = 0.05
    while NOISE < 1:
        # Defined constants to test
        
        # FILENAME = 'Green_Eggs_and_Ham.txt'
        # FILENAME = 'Harry_Pottter_and_the_Sorcerer.txt'
        # FILENAME = 'Slaughterhouse_Five.txt'
        FILENAME = 'stanford.png'
        PACK_SIZE = 180
        NUM_TRIALS = 20

        times = []
        numReceived = []
        numSent = []
        matches = []
        fReceived = open('./stats/' + 'numReceived.txt', "w+")
        fSent = open('./stats/' + 'numSent.txt', "w+")
        for i in range(NUM_TRIALS):
            start = time.time()
            run(FILENAME, NOISE, PACK_SIZE, fReceived, fSent, matches)
            end = time.time()
            times.append(end-start)
        fReceived.close()
        fSent.close()

        fReceived = open('./stats/' + 'numReceived.txt', "r")
        fSent = open('./stats/' + 'numSent.txt', "r")
        numReceived = [int(x) for x in fReceived.readlines()]
        numSent = [int(x) for x in fSent.readlines()]
        fReceived.close()
        fSent.close()
        # output results
        print('Both Sender and Receiver have exited')
        if filecmp.cmp('./resources_to_send/' + FILENAME, './resources_received/' + FILENAME):
            print('Sent and received files match!')
        else:
            print('Sent and received files differ')

        # print numSent
        # print numReceived 
        print '========================================'
        print 'NOISE:', NOISE
        print 'Average time per trial: ', sum(times)/len(times)
        print 'Average number of sent packets: ', sum(numSent)/len(numSent)
        print 'Average number of received packets: ', sum(numReceived)/len(numReceived)
        print 'Percentage of complete transmissions: ', 100*sum(matches)/NUM_TRIALS,'%'
        ans.append([
            NOISE, sum(times)/len(times), sum(numSent)/len(numSent), sum(numReceived)/len(numReceived), 100*sum(matches)/NUM_TRIALS
        ])

        NOISE += STEP_SIZE
    f = open(FILENAME[:-4] + 'rq.txt', 'w')
    f.write(str(ans))
    f.close()