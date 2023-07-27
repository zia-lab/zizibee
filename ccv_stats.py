#!/usr/bin/env python

import subprocess
import numpy as np
import matplotlib.pyplot as plt
import sys

opt = sys.argv[1]

def oscar_users():
    '''
    Get the names of the users currently using OSCAR.

    Parameters
    ----------
    None
    
    Returns
    -------
    (users, cpus) (list, list): with the users and how many cores they are using
    '''
    users = []
    cpus = []
    allq_raw = (subprocess.check_output("allq",shell=True)).decode().split('\n')
    for line in allq_raw:
        line_parts = line.split()
        if len(line_parts)==8:
            users.append(line_parts[3])
            cpus.append(int(line_parts[4]))
    users = np.array(users)
    cpus = np.array(cpus)
    unique_users = np.array(sorted(list(set(users))))
    num_jobs = np.array([sum(users==k) for k in unique_users])
    num_cpus = np.array([sum(cpus[users==us]) for us in unique_users])
    sorter = np.argsort(-num_cpus)
    return (unique_users[sorter], num_cpus[sorter])

ou = oscar_users()

if opt == 'graph':
    fig, ax = plt.subplots(figsize=(10,20))
    ax.barh(np.arange(len(ou[1])),ou[1])
    ax.set_ylim(-0.5,len(ou[1]))
    ax.set_yticks(np.arange(len(ou[1])))
    ax.set_yticklabels(ou[0])
    ax.set_title("Users @ OSCAR")
    ax.set_xlabel("# CPUS")
    plt.savefig('OSCAR-Usage.png')
    plt.show()
else:
    for index in range(len(ou[0])):
        print('%s\t%d'%(ou[0][index], ou[1][index]))
