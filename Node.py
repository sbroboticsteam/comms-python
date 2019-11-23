import json
import zmq
import traceback
import struct


class Node():
    """This is the class that will be the base of every node object

    Each node will read a config file in JSON format to initialize zmq sockets.
    The sockets will be stored in a dict with the key being the topic and the
    value being the socket.
    To create a node, make a config file and extend the run() method.
    Further functionality is on the way.
    """

    def __init__(self, configPath):
        f = open(configPath)
        self.configPath = configPath
        self.configData = json.load(f)
        f.close()
        self.id = self.configData['id']
        self.context = zmq.Context()
        self.topics = {}
        self.initzmq()

    def stopzmq(self):
        """ Shuts down all zmq stuff


        """

        self.context.destroy()

    def loop(self):
        """ The main node code that gets executed every loop

        This is the method that should be overridden for the node to do stuff
        So help me God if anyone overrides this and puts a while true in there
        """

        print(self.id + " needs an overridden loop method")

    # TODO: use new helper methods
    def initzmq(self):
        """This method initializes zmq sockets and places them in the topics dict

        It will throw exceptions if the JSON it was fed is not correct
        """

        if "topics" not in self.configData:
            raise Exception("Topics not found in %s" % self.configPath)

        for topic in self.configData['topics']:
            addr = self.gen_address(topic['protocol'], topic['address'],
                                    topic['port'])
            socket = self.build_socket(topic['paradigm'], topic['topic'], addr)
            self.topics[topic['name']] = socket

    def gen_address(self, protocol, address, port):
        """ This method builds a url from info in a json file

        It can create a url for ipc, udp and tcp.
        It will throw exceptions if the protocol is invalid
        """

        url = ""

        if protocol == "tcp":
            url = "tcp://"
        elif protocol == "udp":
            url = "udp://"
        elif protocol == "ipc":
            url = "ipc://"
        else:
            raise Exception("Protocol not ipc or udp or tcp")

        url += address

        if protocol == "tcp" or protocol == "udp":
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
            socket == self.context.socket(zmq.REP)
            socket.bind(url)
        else:
            raise Exception("Please provide a valid paradigm")

        return socket

    def send(self, topic, msg):
        """This method can be used to send messages for the pub pattern

        The first argument is the topic to send the message on and the second
        is the message body
        """
        if isinstance(msg, np.ndarray):
            """
            send numpy array as 1 + np type + np dimension + np shape + np data
            """
            out = bytes([1]) + str(msg.dtype).encode() + bytes([len(msg.shape)]) + bytes(msg.shape) + msg.tobytes()
            self.topics[topic].send(out)
        elif isinstance(msg, json):
            """
            send json
            """
            out = bytes([2]) + ' '.join(format(ord(letter), 'b') for letter in str)
            self.topics[topic].send(out)
        elif isinstance(msg, int):
            """
            send integer
            """
            out = bytes([3]) + msg.to_bytes(4, byteorder="big", signed=True)
            self.topics[topic].send(out)
        elif isinstance(msg, float):
            """
            send float
            """
            out = bytes([4]) + struct.pack('d', msg)
            self.topics[topic].send(out)
        elif isinstance(msg, bool):
            """
            send boolean
            """
            out = bytes([5]) + struct.pack('?', msg)
            self.topics[topic].send(out)
        else:
            """
            send everything else as a string
            """
            out = bytes([6])
            out = "%s %s" % (topic, msg)
            self.topics[topic].send(out.encode())

    def recv(self, topic):
        """This method is used to receive messages without a callback
            It decodes the received bytes to turn into data
        """
        re = self.topics[topic].recv()

        data_type = re[0]

        if data_type == 1: # receive np array
            return 0
        elif data_type == 2: # receive json
            return json.dumps(re[1:].decode()).replace("'", '"')[1:-1]
        elif data_type == 3: # receive integer
            return re[1:].from_bytes(4, byteorder="big", signed=True)
        elif data_type == 4: # receive float
            return struct.unpack('d', re[1:])[0]
        elif data_type == 5: # receive bool
            return struct.unpack('?', re[1:])[0]
        else:
            re.decode()
        

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
        self.topics[topic].send(req)
        msg = self.topics[topic].recv()
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
        
        msg = self.topics[topic].recv()
        rep = callback(msg)
        self.topics[topic].send(rep)
