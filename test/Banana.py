import sys
sys.path.insert(1, '..')
from Host import Host


class Banana(Host):
    
    name = 'banana'

    def run(self):
        msg = self.node.recv_simple('juice')
        print()
        print("Message received:")
        print(msg)
        print()
