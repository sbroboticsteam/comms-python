
import sys
sys.path.insert(1, '..')
from Host import Host
import numpy as np

class Recv(Host):
    name = 'recv'
    def printr(self, ma):
        print(ma.shape)
        print(ma)

    def run(self):
        self.node.request("matrix", bytes("test", 'utf-8'), self.printr)
