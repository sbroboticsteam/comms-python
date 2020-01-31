import sys
sys.path.insert(1, '..')
from Host import Host


class Apple(Host):
    
    name = 'apple'

    def run(self):
        # self.node.print_topics()
        self.node.send('juice', "Hey banana")
        self.node.send('smoothie', "Heyyo banana!")
