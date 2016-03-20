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
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya

# Plug-in information:
kPluginNodeName = "corollary"
kPluginNodeId = OpenMaya.MTypeId(0xBEFF8)


class CorollaryNode(OpenMayaMPx.MPxDeformerNode):
    inflation_attr = OpenMaya.MObject()

    def deform(self, data, iterator, matrix, index):
        """Deform each vertex using the geometry iterator"""

        # Values
        envelope = data.inputValue(
            OpenMayaMPx.cvar.MPxDeformerNode_envelope).asFloat()
        inflation = data.inputValue(self.inflation_attr).asDouble()

        # Get normal
        input_attribute = OpenMayaMPx.cvar.MPxDeformerNode_input
        input_geometry_attribute = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom

        input_handle = data.outputArrayValue(input_attribute)
        input_handle.jumpToElement(index)
        input_geometry_object = input_handle.outputValue().child(
            input_geometry_attribute).asMesh()

        normals = OpenMaya.MFloatVectorArray()
        mesh_fn = OpenMaya.MFnMesh(input_geometry_object)
        mesh_fn.getVertexNormals(True, normals, OpenMaya.MSpace.kTransform)

        points = OpenMaya.MPointArray()
        mesh_fn.getPoints(points, OpenMaya.MSpace.kTransform)

        positions = []
        for index in xrange(points.length()):
            positions.append([points[index][0],
                              points[index][1],
                              points[index][2]])

        # send data..
        # ...
        # retrieve data..

        points = OpenMaya.MPointArray()
        for pos in positions:
            points.append(*pos)

        index = 0
        while not iterator.isDone():
            vertex_index = iterator.index()
            normal = OpenMaya.MVector(normals[vertex_index])
            point = points[index] + (
                normal *
                inflation *
                envelope *
                0.1
            )

            iterator.setPosition(point)
            iterator.next()
            index += 1


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(CorollaryNode())


def nodeInitializer():
    # The following MFnNumericAttribute function set
    # will allow us to create our attributes.
    numeric_attribute_fn = OpenMaya.MFnNumericAttribute()

    # Define a mesh inflation attribute, responsible for actually
    # moving the vertices in the direction of their normals.
    CorollaryNode.inflation_attr = numeric_attribute_fn.create(
        "meshInflation", "mi", OpenMaya.MFnNumericData.kDouble, 10.0)
    numeric_attribute_fn.setStorable(True)
    numeric_attribute_fn.setWritable(True)
    numeric_attribute_fn.setKeyable(True)
    numeric_attribute_fn.setReadable(False)
    CorollaryNode.addAttribute(CorollaryNode.inflation_attr)

    # If any of the inputs change, the output mesh will be recomputed.
    CorollaryNode.attributeAffects(
        CorollaryNode.inflation_attr,
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
