"""An XMLRPC-based deformer"""

import math
from SimpleXMLRPCServer import SimpleXMLRPCServer


def compute(positions, data):
    for pos in positions:
        value = math.sin(pos[0] * data["frequency"] + data["offset"])
        value *= data["amplitude"]
        value *= data["envelope"]
        pos[1] += value  # modify Y-coordinate
    return positions


server = SimpleXMLRPCServer(("127.0.0.1", 7070))
server.register_function(compute)
print("Listening on 127.0.0.1:7070")
server.serve_forever()
