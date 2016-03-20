"""Copy the following lines and run them in Maya's Python Script Editor:

import maya.cmds as cmds

def load():
    cmds.loadPlugin("mayaCorollaryPlugin.py")

def unload():
    existing = cmds.ls(type="corollary")
    cmds.delete(existing) if existing else None
    cmds.flushUndo()
    cmds.unloadPlugin("mayaCorollaryPlugin")

load()

cmds.polySphere()
cmds.deformer(type="corollary")

unload()

"""

import sys
import json
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya

# Third-party
import zmq

# Plug-in information:
kPluginNodeName = "corollary"
kPluginNodeId = OpenMaya.MTypeId(0xBEFF8)


class CorollaryNode(OpenMayaMPx.MPxDeformerNode):
    amplitude_attr = OpenMaya.MObject()
    offset_attr = OpenMaya.MObject()

    def __init__(self):
        super(CorollaryNode, self).__init__()

        context = zmq.Context()

        print("Connecting to server")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:7070")

        self.socket = socket

    def deform(self, data, iterator, matrix, index):
        """Deform each vertex using the geometry iterator"""

        # Values
        envelope = data.inputValue(OpenMayaMPx.cvar.MPxDeformerNode_envelope)
        amplitude = data.inputValue(self.amplitude_attr)
        offset = data.inputValue(self.offset_attr)

        # Get normal
        input_attribute = OpenMayaMPx.cvar.MPxDeformerNode_input
        input_geometry_attribute = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom

        input_handle = data.outputArrayValue(input_attribute)
        input_handle.jumpToElement(index)
        input_geometry_object = input_handle.outputValue().child(
            input_geometry_attribute).asMesh()

        points = OpenMaya.MPointArray()
        mesh_fn = OpenMaya.MFnMesh(input_geometry_object)
        mesh_fn.getPoints(points, OpenMaya.MSpace.kTransform)

        positions = []
        for index in xrange(points.length()):
            positions.append([
                points[index][0],
                points[index][1],
                points[index][2]
            ])

        # send data..
        self.socket.send(json.dumps({
            "positions": positions,
            "data":  {
                "envelope": envelope.asFloat(),
                "amplitude": amplitude.asDouble(),
                "offset": offset.asDouble(),
            }
        }))

        positions = json.loads(self.socket.recv())

        # Convert Python floats to MPointArray
        points = OpenMaya.MPointArray()
        for pos in positions:
            points.append(*pos)

        while not iterator.isDone():
            iterator.setPosition(points[iterator.index()])
            iterator.next()


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(CorollaryNode())


def nodeInitializer():
    amplitude_fn = OpenMaya.MFnNumericAttribute()
    offset_fn = OpenMaya.MFnNumericAttribute()

    CorollaryNode.amplitude_attr = amplitude_fn.create(
        "amplitude", "am", OpenMaya.MFnNumericData.kDouble, 10.0)
    amplitude_fn.setStorable(True)
    amplitude_fn.setWritable(True)
    amplitude_fn.setKeyable(True)
    amplitude_fn.setReadable(False)
    CorollaryNode.addAttribute(CorollaryNode.amplitude_attr)

    CorollaryNode.offset_attr = offset_fn.create(
        "offset", "of", OpenMaya.MFnNumericData.kDouble, 10.0)
    offset_fn.setStorable(True)
    offset_fn.setWritable(True)
    offset_fn.setKeyable(True)
    offset_fn.setReadable(False)
    CorollaryNode.addAttribute(CorollaryNode.offset_attr)

    # If any of the inputs change, the output mesh will be recomputed.
    CorollaryNode.attributeAffects(
        CorollaryNode.amplitude_attr,
        OpenMayaMPx.cvar.MPxDeformerNode_outputGeom)

    CorollaryNode.attributeAffects(
        CorollaryNode.offset_attr,
        OpenMayaMPx.cvar.MPxDeformerNode_outputGeom)


def initializePlugin(mobject):
    """Initialize the plug-in """
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(
            kPluginNodeName,
            kPluginNodeId,
            nodeCreator,
            nodeInitializer,
            OpenMayaMPx.MPxNode.kDeformerNode
        )
    except:
        sys.stderr.write("Failed to register node: " + kPluginNodeName)
        raise


def uninitializePlugin(mobject):
    """Uninitializes the plug-in """
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(kPluginNodeId)
    except:
        sys.stderr.write("Failed to deregister node: " + kPluginNodeName)
        raise
