
from Node import Node
import serial
import json
from numpy import interp
import time

ser = serial.Serial()
ser.port = "/dev/ttyACM1"
ser.baudrate = 115200
ser.write_timeout = 1

ser.open()

node = Node("test_node.json")

while True:
    msg = node.recv_simple("inputs-out")
    dmsg = json.loads(msg[11:])
    out = [bytes([int(interp(dmsg[1], [-32768, 32768], [255, 0]))])[0], bytes([int(interp(dmsg[4], [-32768, 32768], [255,0]))])[0], bytes([int(dmsg[7])])[0]]
    
    try:
        ser.write(bytearray(out))
        ser.write(bytearray('\n'))
    except Exception:
        print("timeout")
        pass
    time.sleep(0.01)

    print(bytearray(out))
    
    

