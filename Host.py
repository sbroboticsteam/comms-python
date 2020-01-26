from Node import Node


class Host():
    """ This is the class that needs to be extended by every zmq-using routine.

    Each routine must override exactly two things:
    1. The name attribute: 
        the host's name in the config file.
    2. The run method: 
        treat this method as the starting point of the routine's script.
    (important: do not override __init__)

    All hosts will be set up & started automatically by a starter script. By 
    the time each host's run method is called, all zmq sockets will be 
    initialized, and each host will have a fully set-up Node object as an 
    attribute (self.node) that can be used for message passing.
    """
    
    name = None

    def __init__(self, config):
        if self.name is None:
            raise Exception("Didn't extend Host or override name attribute")
        if not isinstance(self.name, str):
            raise Exception("Invalid value for the name attribute")
        self.node = Node(self.name, config)

    def run(self):
        """This method is meant to be overridden
        
        """
        print("The run method must be overridden")
