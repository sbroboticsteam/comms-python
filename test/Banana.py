import sys
sys.path.insert(1, '..')
from Host import Host


class Banana(Host):
    
    name = 'banana'

    def run(self):
        msg = self.node.recv_simple('smoothie')
        print("Message received:")
        print(msg)
        msg = self.node.recv_simple('juice')
        print("Message received:")
        print(msg)
