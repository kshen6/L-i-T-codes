from __future__ import division
import math

def ideal_soliton(N, **kwargs):
    '''
    generate list of probabilities corresponding to ideal
    soliton distribution
    :param N - number of total buckets
    '''
    p = [1 / N] + [1 / ((k + 1) * k) for k in range(1, N)]
    return p

def robust_soliton(N, **kwargs):
    '''
    generate list of probabilities corresponding to robust
    soliton distribution
    :param N - number of total buckets
    :param M - integer < N where there will be another spike
    :param d - failure probability
    '''
    M, d = kwargs['M'], kwargs['d']
    R = N / M
    t = [0] * N
    for i in range(1, M):
        t[i - 1] = 1 / (i * M)
    t[M - 1] = math.log(R / d) / M
    # the rest are zeros
    p = ideal_soliton(N)
    norm = sum(p) + sum(t)
    y = [(a + b) / norm for a, b in zip(p, t)]
    return y