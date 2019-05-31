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
    def __init__(self, data, degree, seed):
        self.data = data
        self.degree = degree
        self.seed = seed
    
    def recover_source(self, num_blocks):
        '''
        Using degree and random seed, recover the indices of blocks that
        were xor'd together to generate data
        '''
        random.seed(self.seed)
        indices = random.sample(list(range(1, num_blocks + 1)), self.degree)
        self.indices = indices

class Encoder():
    def __init__(self, data, soliton):
        self.data = data
        self.soliton = soliton
    
    def create_blocks(self, block_size):
        blocks = np.array_split(self.data, len(self.data) // block_size)
        self.blocks = blocks
    
    def encode(self):
        num = len(self.blocks)
        indices = np.random.choice(list(range(1, num + 1)), num, p=self.soliton(num))
        res = self.blocks[indices[0]]
        for i in range(1, len(indices)):
            res ^= self.blocks[indices[i]]
        yield Packet(res, indices)

class Fountain():
    def __init__(self, network):
        self.network = network
    
    def send_over_network(self):
        raise NotImplementedError()

class Decoder():
    def __init__(self, stream):
        self.stream = stream
    
    def decode(self):
        raise NotImplementedError()