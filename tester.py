import numpy as np
import time
from itertools import product
import sympy as sp

info='''┌────────────────────────────────────────────────────────────────────────┐
│~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~│
│~~~~                                                                ~~~~│
│~~~~     This is a benchmark useful to compare the single-core      ~~~~│
│~~~~    performance of different machines and configs. It runs a    ~~~~│
│~~~~ sequence of common tasks using numpy and sympy. The total time ~~~~│
│~~~~ these take is compared against a standard time of 0.292 s. The ~~~~│
│~~~~         higher the score, the faster the machine/task.         ~~~~│
│~~~~                                                                ~~~~│
│~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~│
└────────────────────────────────────────────────────────────────────────┘'''
version="0.2"
title="### WaveS benchmark v %s ###" % version

# these are used for averaging out as many runs
repeats=20

# these standard times are from an M1 Pro MacBook Pro with 16 GB of RAM

standard_times = {'fft': 0.018051999999997292,
 'eig': 0.027115000000002,
 'rando': 0.02647800000000089,
 'multi': 0.03607099999999974,
 'matinv': 0.003328999999997251,
 'sorter': 0.047008000000001715,
 'itersum': 0.06371399999999738,
 'funceval': 0.03203800000000001,
 'symbexpand': 0.034727000000000174,
 'total': 0.28853199999999646}

def fft():
    for i in range(10):
        ft = np.fft.fft(np.random.random(100000))

def eig():
    for i in range(10):
        eigvs = np.linalg.eigvals(np.random.random((100,100)))

def rando():
    randos = np.random.random((2000,2000))
    return randos

def multi():
    a0 = np.random.random((100,100))
    a1 = np.random.random((100,100))
    for i in range(10000):
        b = a0 * a1

def matinv():
    m0 = np.random.random((100,100))
    for i in range(10):
        np.linalg.inv(m0)

def sorter():
    ar = np.random.random(10000)
    for _ in range(100):
        np.sort(ar)

def itersum():
    it = range(100)
    summa = 0
    for i0, i1, i2 in product(it, it, it):
        summa += i0+i1+i2

def funceval():
    funcs = [np.sin, np.cos, np.tan, lambda x: 1/x, np.log10, np.log2]
    theta = np.linspace(0.1,2*np.pi,1000000)
    for func in funcs:
        func(theta)

def symbexpand():
    monos = [np.random.randint(0,10)*sp.Symbol('x')+np.random.randint(1,10) for _ in range(20)]
    poly = sp.S(1)
    for mono in monos:
        poly = poly*mono
    sp.expand(poly)

benchmarks = {'fft': fft, 'eig': eig, 'rando': rando,
              'multi': multi, 'matinv': matinv, 'sorter': sorter,
              'itersum': itersum, 'funceval': funceval,
              'symbexpand': symbexpand}

def benchman(repeats):
    '''
    Standard score is 1000, which is performance of 2021 MacBook Pro 16".
    '''
    tw = 30
    print('-'*tw)
    print(title)
    print('-'*tw)
    msg = "{:<10}\t{:<4}\t{:>5}".format("task", "t/s", "score")
    print(msg)
    print('-'*tw)
    timings = {}
    scores = {}
    for bench, benchfun in benchmarks.items():
        # print('%s ... ' % bench, end='')
        times = []
        for rep in range(repeats):
            start_time = time.process_time()
            benchfun()
            elapsed_time = time.process_time() - start_time
            times.append(elapsed_time)
        elapsed_time = np.mean(elapsed_time)
        score = int(round(1000 * standard_times[bench]/elapsed_time))
        msg = '%.3f s | (%d/1000)' % (elapsed_time, score)
        msg = "{:<10}\t{:<.4f}\t{:>5}".format(bench, elapsed_time, score)
        print(msg)
        timings[bench] = elapsed_time
        scores[bench] = score
    timings['total'] = sum(timings.values())
    timings['score'] = np.round(1000 * standard_times['total'] / timings['total'])
    print('-'*tw)
    print('TOTAL TIME = %.2f s' % timings['total'])
    print('TOTAL SCORE = %d / 1000' % timings['score'])
    print('-'*tw)
    return timings

if __name__ == '__main__':
    print(info)
    timings = benchman(repeats)
