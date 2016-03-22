import os
import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

with open(os.path.join(os.path.dirname(__file__), "test_data.json")) as f:
    data = json.load(f)

socket.send(json.dumps(data))

recv = json.loads(socket.recv())

for index, position in enumerate(recv["positions"]):
    print "%s : %s" % (position[1], data["positions"][index][1])
