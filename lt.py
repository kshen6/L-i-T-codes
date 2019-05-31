import numpy as np
import random
'''
LT code stuff
partially inspired by Spriteware, at https://github.com/Spriteware/lt-codes-python
'''

class Packet():
    '''
    Structure to encapsulate information about each packet
    :param data - store the xor'd information
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
        indices = random.sample(list(range(1, self.num_blocks + 1)), self.degree)
        self.indices = indices

class Encoder():
    def create_blocks(self, data, blk_sz, pad_with=0):
        '''
        divide data into blocks of tunable size
        :param blk_sz - desired block size
        :param pad_with - if size of data is not evenly divisible, ensure that all
            blocks are of the same size
        '''
        self.data = data
        blocks = [self.data[i:i + blk_sz] for i in range(0, len(self.data), blk_sz)]
        blocks[-1] += [0] * (blk_sz - len(blocks[-1]))
        self.blocks = blocks
    
    def encode(self, seed, soliton, num_to_transmit = float('inf')):
        '''
        generator function to indefinitely produce xor'd Packets
        :param seed - random seed for recovering indices
        :param soliton - desired degree distribution
        must call create_blocks before calling this function
        '''
        assert hasattr(self, 'blocks'), 'Must call create_blocks to initialize'

        counter = 0
        while counter < num_to_transmit:
            num_blocks = len(self.blocks)
            # choose a degree based on the given soliton distribution
            degree = np.random.choice(list(range(1, num_blocks + 1)), num_blocks, \
                p=soliton(num_blocks))
            # seed so that we can recover the source block indices
            random.seed(seed)
            indices = random.sample(list(range(1, num_blocks + 1)), degree)
            # XOR all blocks
            block = self.blocks[indices[0]]
            for b in indices[1:]:
                block ^= self.blocks[b]
            yield Packet(block, degree, num_blocks, seed)
            # do not duplicate seeds
            seed += 1
            counter += 1

class Decoder():
    def __init__(self, num_blocks):
        self.received = []
        self.belief = [None] * num_blocks
        self.num_blocks = num_blocks
    
    def incorporate(self, packet):
        packet.recover_source()
        self.received.append(packet)
        if len(self.received) >= self.num_blocks:
            self.propagate_beliefs([-1])
    
    def propagate_beliefs(self, index = None):
        if all(s is None for s in self.belief):
            # beginning our belief - search for symbol with degree 1
            deg_one_symbols = [(i, r) for i, r in enumerate(self.received) if r.degree == 1]
            if len(deg_one_symbols) == 0: # decoding failed
                raise "decoding failed, no point of entry"
            for _, s in deg_one_symbols:
                self.belief[s.indices[0]] = s.data
            index = [item[0] for item in deg_one_symbols]
        for item in index:
            for i, r in enumerate(self.received):
                if r == item:
                    pass
                if item in r.indices:
                    r.data ^= self.received[item].data
                    r.indices.remove(item)