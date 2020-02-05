
import sys
sys.path.insert(1, '..')
from Host import Host
import numpy as np

class Recv(Host):
    name = 'recv'
    
    def run(self):
        ar = self.node.recv_simple("matrix")
        print("recevied:")
        print(ar)
