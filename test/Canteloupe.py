import sys
sys.path.insert(1, '..')
from Host import Host


class Canteloupe(Host):
    
    name = 'canteloupe'

    def generate_response(self, msg):
        return bytes("I received your message: {}".format(msg.decode('utf-8')), 'utf-8')

    def run(self):
        self.node.reply("zest", self.generate_response)
