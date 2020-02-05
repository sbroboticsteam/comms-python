import json
import zmq
import traceback
import numpy as np

def extract_config(name, file):
    # read master config from file
    f = open(file)
    master = json.load(f)
    f.close()
    # make sure host exists in master config
    if name not in master['hosts']:
        raise Exception("Host with given name does not exist")
    config = {'pub': [], 'sub': [], 'req': [], 'rep': []}
    # iterate each topic in master config:
    for topic in master['topics']:
        # copy topic info
        newtopic = {
            'id': topic['id'],
            'protocol': topic['protocol'],
            'address': topic['address'],
            'port': ""
        }
        if topic['protocol'] == 'tcp':
            newtopic['port'] = topic['port']
        # add topic to the correct list (if any)
        if topic['paradigm'] == 'pubsub':
            if topic['pub'] == name:
                config['pub'].append(newtopic)
            elif name in topic['sub']:
                config['sub'].append(newtopic)
        elif topic['paradigm'] == 'reqrep':
            if topic['req'] == name:
                config['req'].append(newtopic)
            elif topic['rep'] == name:
                config['rep'].append(newtopic)
        else: 
            raise Exception("Invalid paradigm")
    return config


class Node():
    """ This is the class that manages a host's zmq sockets.

    You do not need to create any nodes; they will be created automatically by
    the Host class.
    """

    def __init__(self, name, config):
        self.name = name
        self.config_data = extract_config(name, config)
        self.context = zmq.Context()
        self.pub = {}
        self.sub = {}
        self.req = {}
        self.rep = {}
        self.initzmq()

    def initzmq(self):
        """ This method initializes zmq sockets for topics on which the node is
        pub or rep.

        """

        self.build_sockets('pub')
        self.build_sockets('sub')
        self.build_sockets('rep')
        self.build_sockets('req')

    def stopzmq(self):
        """ Shuts down all zmq stuff

        """

        self.context.destroy()
    
    def build_sockets(self, paradigm):
        for topic in self.config_data[paradigm]:
            addr = self.gen_address(topic['protocol'], topic['address'], 
                                    topic['port'])
            socket = self.build_socket(paradigm, topic['id'], addr)
            if paradigm == 'pub':
                self.pub[topic['id']] = socket
            elif paradigm == 'sub':
                self.sub[topic['id']] = socket
            elif paradigm == 'req':
                self.req[topic['id']] = socket
            elif paradigm == 'rep':
                self.rep[topic['id']] = socket

    def gen_address(self, protocol, address, port):
        """ This method builds a url from info in a json file

        It can create a url for ipc and tcp.
        It will throw exceptions if the protocol is invalid
        """

        url = ""

        if protocol == "tcp":
            url = "tcp://"
        elif protocol == "ipc":
            url = "ipc://"
        else:
            raise Exception("Protocol not ipc or tcp")

        url += address

        if protocol == "tcp":
            url += ":" + port

        return url

    def build_socket(self, paradigm, topic, url):
        """ This method creates a socket from a paradigm and a url

        """

        socket = None
        if paradigm == "sub":
            socket = self.context.socket(zmq.SUB)
            socket.connect(url)
            socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        elif paradigm == "pub":
            socket = self.context.socket(zmq.PUB)
            socket.bind(url)
        elif paradigm == "req":
            socket = self.context.socket(zmq.REQ)
            socket.connect(url)
        elif paradigm == "rep":
            socket = self.context.socket(zmq.REP)
            socket.bind(url)
        else:
            raise Exception("Please provide a valid paradigm")

        return socket

    def send(self, topic, msg):
        """This method can be used to send messages for the pub pattern

        The first argument is the topic to send the message on and the second
        is the message body
        """
        if topic not in self.pub:
            raise Exception("Topic is not an existing pub topic")
        out = "" 
        if isinstance(msg, np.ndarray):
            """
            send numpy array as 1 + np type + np dimension + np shape + np data
            """
            out = bytes([1]) + bytes([0]) + str(msg.dtype).encode() + bytes([0]) + len(msg.shape).to_bytes(4, byteorder="big")
            for i in msg.shape:
                out += i.to_bytes(4, byteorder="big")
            out += msg.tobytes()
            self.pub[topic].send(out)
        else:
            out = "%s %s" % (topic, msg)
            self.pub[topic].send(bytes(2) + bytes(out, 'utf-8'))

    def recv_simple(self, topic):
        """This method is used to receive messages without a callback
        
        It returns a string read from the topic
        """
        if topic not in self.sub:
            raise Exception("Topic is not an existing sub topic")
        re = self.sub[topic].recv()

        data_type = re[0]

        if data_type == 1: # receive np array

            """
            recv numpy array as 1 + np type + np dimension + np shape + np data
            """
            # get type
            t = np.dtype(re.split(bytes([0]),2)[1].decode("utf-8"))
            # get dimentions
            aftertype = re.split(bytes([0]),2)[2]
            d = int.from_bytes(aftertype[:4], byteorder="big")
            # get shape
            shape = []
            for i in range(d):
                shape.append(int.from_bytes(aftertype[i*4 + 4: i*4 + 8], byteorder="big"))
            shape = tuple(shape)
            array = np.frombuffer(aftertype[d*4 + 4:], dtype = t)
            array = array.reshape(shape)
            return array
        else:
            return re[1:]

    # TODO: implement a timeout
    def recv(self, topic, callback):
        """This method is used to receive messages for the sub pattern

        The first argument is the topic to look for messages on.
        The second argument is a function to be executed with the message
        received being passed to it as an argument
        NOT VERIFIED: This method is blocking, and will interrupt execution
        until a message is received
        """
        if topic not in self.sub:
            raise Exception("Topic is not an existing sub topic")
        re = self.sub[topic].recv_string()
        callback(re)

    def request(self, topic, req, callback):
        """This method is used to send a request to a node

        The first argument is the topic(in this case, the node) to send a
        request to.
        The second argument is the request to send
        The third argument is a callback function to process the reply from
        the server. The reply will be a string.
        IMPORTANT: this method calls recv() and send(), so the parameters must
        be bytes!
        """
        if topic not in self.req:
            raise Exception("Topic is not an existing req topic")
        self.req[topic].send(req)
        msg = self.req[topic].recv()
        callback(msg)

    def reply(self, topic, callback):
        """This method is used to send a reply to a node

        The first argument is the topic(in this case, the node) to reply to
        The second argument is a callback that will handle the request sent to
        this node. It must return a string.
        The reply generated by the callback is sent as a reply to the node
        that sent a request
        IMPORTANT: this method calls recv() and send(), so the parameters must
        be bytes!
        """
        
        if topic not in self.rep:
            raise Exception("Topic is not an existing rep topic")
        msg = self.rep[topic].recv()
        rep = callback(msg)
        self.rep[topic].send(rep)

    def print_topics(self):
        """This method prints the configs of each topic.

        """

        print("Host name: {}".format(self.name))
        print(" pub:")
        for topic in self.pub:
            print("  " + topic)
        print(" sub:")
        for topic in self.sub:
            print("  " + topic)
        print(" req:")
        for topic in self.req:
            print("  " + topic)
        print(" rep:")
        for topic in self.rep:
            print("  " + topic)
