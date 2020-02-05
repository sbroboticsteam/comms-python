
import multiprocessing as mp
import time
from recv import Recv
from send import Send
MASTERCONFIG = "./matrix.json"
HOSTS = [Recv, Send]


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
    
    time.sleep(1)
    trigger.put('all setup complete')

    for proc in procs:
        proc.join()
