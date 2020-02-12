from Node import Node
import numpy as np

import sys
sys.path.insert(1, '..')
from Host import Host
import numpy as np

class Send(Host):
    name = 'send'
    a = np.array([[10,10,39],[20,30,40]])
    
    def respond(self, msg):
        return self.a

    def run(self):
        print("sending...")
        self.node.reply('matrix', self.respond)
        print("sent")
        

