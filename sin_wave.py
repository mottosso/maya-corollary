import zmq
import json
import math
import signal

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:7070")

# Enable exiting via CTRL-C
signal.signal(signal.SIGINT, signal.SIG_DFL)


def compute(positions, data):
    for pos in positions:
        value = math.sin(pos[0] * data["amplitude"] + data["offset"])
        value *= data["envelope"]
        pos[1] += value  # modify Y-coordinate
    return positions


print("Listening at tcp://localhost:7070..")
while True:
    #  Wait for next request from client
    data = json.loads(socket.recv())

    #  Send reply back to client
    socket.send(json.dumps(compute(**data)))
