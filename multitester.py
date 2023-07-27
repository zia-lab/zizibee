import numpy as np
import time
from itertools import product
import sympy as sp
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import os

info='''┌────────────────────────────────────────────────────────────────────────┐
│~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~│
│~~~~                                                                ~~~~│
│~~~~     This is a benchmark useful to compare the multi-core       ~~~~│
│~~~~    performance of different machines and configs. It runs a    ~~~~│
│~~~~ sequence of common tasks using numpy and sympy. The total time ~~~~│
│~~~~ these take is compared against a standard time of 0.292 s. The ~~~~│
│~~~~         higher the score, the faster the machine/task.         ~~~~│
│~~~~                                                                ~~~~│
│~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~│
└────────────────────────────────────────────────────────────────────────┘'''
version="0.2"
title="### PWave Benchmark v %s ###" % version

avg_repeats = 3

# these standard times were obtained in a CCV
# machine with 48 cores and 128 GB of RAM
standard_times ={'fft': 0.32651286000000024, 
                 'eig': 0.12225043699999993, 
                 'rando': 0.7260819329999997, 
                 'multi': 0.44948653200000166, 
                 'matinv': 0.11934472299999754, 
                 'sorter': 0.1372562859999995, 
                 'itersum': 0.11692912399999855, 
                 'funceval': 0.11214731899999819, 
                 'symbexpand': 0.11132485099999911, 
                 'total': 2.2213340649999944}

mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')  # e.g. 4015976448
mem_gib = int(mem_bytes/(1024.**3))

def poolrun(fun, reps):
    with ProcessPoolExecutor() as executor:
        # print(f'Using {executor._max_workers} processes.')
        futures = [executor.submit(fun) for _ in range(reps)]
        for future in futures:
            _ = future.result()

def fft():
    '''
    The fast Fourier transform of 100'000 random real numbers.
    '''
    ft = np.fft.fft(np.random.random(100000))
    return ft

def eig():
    '''
    The eigenvalues of a 100x100 random matrix.
    '''
    eigvs = np.linalg.eigvals(np.random.random((100,100)))
    return eigvs

def rando():
    '''
    A 2000x2000 array of random numbers.
    '''
    randos = np.random.random((2000,2000))
    return randos

def multi():
    '''
    Matrix multiplication of two 100x100 random matrices.
    '''
    a0 = np.random.random((100,100))
    a1 = np.random.random((100,100))
    b = a0 * a1
    return b

def matinv():
    '''
    Matrix inversion of a 100x100 random real matrix.
    '''
    m0 = np.random.random((100,100))
    m0i = np.linalg.inv(m0)
    return m0i

def sorter():
    '''
    Sorting 10000 random real numbers.
    '''
    ar = np.random.random(10000)
    ar = np.sort(ar)
    return ar

def itersum():
    '''
    A for loop running a nested sum over one million iterations.
    '''
    it = range(100)
    summa = 0
    for i0, i1, i2 in product(it, it, it):
        summa += i0+i1+i2
    return summa

def funceval():
    '''
    Function evaluation of some common functions.
    '''
    funcs = [np.sin, np.cos, np.tan, lambda x: 1/x, np.log10, np.log2]
    theta = np.linspace(0.1,2*np.pi,1000000)
    for func in funcs:
        func(theta)
    return None

def symbexpand():
    monos = [np.random.randint(0,10)*sp.Symbol('x')+np.random.randint(1,10) for _ in range(20)]
    poly = sp.S(1)
    for mono in monos:
        poly = poly*mono
    polyexp = sp.expand(poly)
    return polyexp

benchmarks = {'fft': (fft, 100),
              'eig': (eig, 100),
              'rando': (rando, 20),
              'multi': (multi, 1000), 
              'matinv': (matinv, 50), 
              'sorter': (sorter,100),
              'itersum': (itersum, 50), 
              'funceval': (funceval,20),
              'symbexpand': (symbexpand,10)}

def benchman(repeats):
    '''
    Standard score is 1000, which is performance of 2021 MacBook Pro 16".
    '''
    tw = 30
    num_cores = multiprocessing.cpu_count()
    print("Using %d cores | %d GB of RAM." % (num_cores, mem_gib))
    print('-'*tw)
    print(title)
    print('-'*tw)
    msg = "{:<10}\t{:<4}\t{:>5}".format("task", "t/s", "score")
    print(msg)
    print('-'*tw)
    timings = {}
    scores = {}
    for bench, (benchfun, reps) in benchmarks.items():
        times = []
        for _ in range(repeats):
            start_time = time.process_time()
            poolrun(benchfun, reps)
            elapsed_time = time.process_time() - start_time
            times.append(elapsed_time)
        elapsed_time = np.mean(elapsed_time)
        score = int(round(1000 * standard_times[bench]/elapsed_time))
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
    timings = benchman(avg_repeats)
    # print(timings)
