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

class Fountain():
    def __init__(self, network):
        self.network = network
    
    def send_over_network(self):
        raise NotImplementedError()

class Decoder():
    def __init__(self):
        self.received = []
        self.belief = []
    
    def incorporate(self, packet):
        self.received.append(packet)
        self.propagate_beliefs()
    
    def propagate_beliefs(self):
        pass

    def decode(self, packets):
        for p in packets:
            p.recover_source()
        self.packets = packets