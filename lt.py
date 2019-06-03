from __future__ import division
import numpy as np
import random
from soliton import ideal_soliton, robust_soliton

def xor(s1, s2):
    '''
    perform component-wise xor (works for any given string)
    '''
    assert len(s1) == len(s2), 'cannot xor if unequal size'
    return ''.join(str(chr(ord(a)^ord(b))) for a,b in zip(s1,s2))

class Packet():
    '''
    Structure to encapsulate information about each packet
    :param data - store the xor'd information
    :param degree - number of input symbols xor'd together
    :param num_blocks - original total number of input symbols
    :param seed - used for recovering indices
    '''
    def __init__(self, data, degree, num_blocks, seed):
        self.data = data
        self.degree = degree
        self.num_blocks = num_blocks
        self.seed = seed

    def recover_source(self):
        '''
        Using degree and random seed, recover the indices of blocks that
        were xor'd together to generate data
        '''
        random.seed(self.seed)
        indices = random.sample(range(self.num_blocks), self.degree)
        self.neighbors = indices

    def __str__(self):
        nei = self.neighbors if hasattr(self, 'neighbors') else None
        return 'packet object data: {} \n degree: {} \n num blocks: '.format(self.data, self.degree) \
            + '{} \n seed: {} \n neighbors: {}'.format(self.num_blocks, \
                self.seed, nei)

class Encoder():
    def create_blocks(self, blocks):
        '''
        initialize data
        '''
        self.blocks = blocks

    def encode(self, seed, soliton, M = None, d = None, num_to_transmit = float('inf')):
        '''
        generator to indefinitely produce xor'd Packets
        :param seed - random seed for recovering indices
        :param soliton - desired degree distribution
        :param M, d - parameters for robust soliton
        :num_to_transmit - number of Packets to generate
        NOTE: must call create_blocks before calling this function
        '''
        assert hasattr(self, 'blocks'), 'Must call create_blocks to initialize'

        counter = 0
        num_blocks = len(self.blocks)
        M = int(num_blocks / 2) # defines the second peak in soliton distribution
        while counter < num_to_transmit:
            # choose a degree based on the given soliton distribution
            degree = np.random.choice(range(1, num_blocks + 1), p=soliton(num_blocks, M=M, d=d))

            # seed so that we can recover the source block indices
            random.seed(seed)
            indices = random.sample(range(num_blocks), degree)

            # XOR all blocks
            block = self.blocks[indices[0]]
            for b in indices[1:]:
                block = xor(block, self.blocks[b])

            yield Packet(block, degree, num_blocks, seed)
            # do not duplicate seeds
            seed += 1
            counter += 1

class Decoder():
    def __init__(self):
        self.received = [] # queue for unsolved packets
        self.belief = [None] # list of original input symbols
        self.num_blocks = None # number of input symbols
        self.num_packets = 0

    def update_belief(self, packet):
        packet.recover_source()
        self.num_packets += 1
        if self.num_blocks is None:
            self.num_blocks = packet.num_blocks
            self.belief = [None] * self.num_blocks
        self.received.append(packet)
        # if self.num_packets % 100 == 0: # to speed up receiving
        self.decode()
    
    def decode(self):
        symbols_n = len(self.received)
        assert symbols_n > 0, 'nothing to do'

        solved_blocks_count = 0
        iteration_solved_count = 0

        while iteration_solved_count > 0 or solved_blocks_count == 0:
            iteration_solved_count = 0

            for i, symbol in enumerate(self.received):
                if symbol.degree == 1:
                    iteration_solved_count += 1
                    bi = symbol.neighbors[0]
                    self.received.pop(i)

                    if self.belief[bi] is not None:
                        continue
                    
                    self.belief[bi] = symbol.data

                    solved_blocks_count += 1

                    for other in self.received:
                        if other.degree > 1 and bi in other.neighbors:
                            other.data = xor(self.belief[bi], other.data)
                            other.neighbors.remove(bi)
                            other.degree -= 1
            # no more degree 1 blocks:               
            if solved_blocks_count == 0:
                return