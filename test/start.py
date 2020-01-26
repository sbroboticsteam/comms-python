"""
This is the code to automatically start up the hosts Apple and Banana in a 
synchronized way.
To make it work for other groups of hosts, you only need to edit the HOSTS
and MASTERCONFIG constants for this file.
The synchronization currently only supports the case where all hosts operate
in separate processes from each other.
"""
import multiprocessing as mp
from Apple import Apple
from Banana import Banana


MASTERCONFIG = './testconf.json'
HOSTS = [Apple, Banana]


def starter(host, probe, trigger):
    x = host(MASTERCONFIG)
    probe.put('setup complete')
    while trigger.empty():
        pass
    x.run()


if __name__ == '__main__':

    probe = mp.Queue()
    trigger = mp.Queue()

    procs = []
    for host in HOSTS:
        proc = mp.Process(target=starter, args=(host, probe, trigger))
        procs.append(proc)

    for proc in procs:
        proc.start()

    for proc in procs:
        probe.get(block=True)
    trigger.put('all setup complete')

    for proc in procs:
        proc.join()