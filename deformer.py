import math
from SimpleXMLRPCServer import SimpleXMLRPCServer


def compute(positions, data):
    for pos in positions:
        pos[1] += math.sin(pos[0] * data["amplitude"] + data["offset"])
    return positions


server = SimpleXMLRPCServer(("127.0.0.1", 7070))
server.register_function(compute)
print("Listening on 127.0.0.1:7070")
server.serve_forever()
