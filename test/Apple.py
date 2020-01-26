import sys
sys.path.insert(1, '..')
from Host import Host


class Apple(Host):
    
    name = 'apple'

    def run(self):
        print()
        self.node.print_topics()
        self.node.send('juice', "Hey banana")
