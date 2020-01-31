import sys
sys.path.insert(1, '..')
from Host import Host


class Durian(Host):
    
    name = 'durian'

    def print_response(self, msg):
        print("Response: {}".format(msg.decode('utf-8')))

    def run(self):
        self.node.request("zest", bytes("Hey Canteloupe!", 'utf-8'), self.print_response)
