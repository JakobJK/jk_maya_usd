from maya import cmds
from maya.api import OpenMaya as om


def get_scene_scale():
    meters_per_unit = cmds.currentUnit(query=True, linear=True)
    return {
        "mm": 0.001,
        "cm": 0.01,  
        "m": 1.0,
        "in": 0.0254,
        "ft": 0.3048,
        "yd": 0.9144,
    }.get(meters_per_unit, 1.0)
    

def get_mobject_from_name(name):
    sel = om.MSelectionList()
    sel.add(name)
    return sel.getDependNode(0)

def create_transform(name, parent):
    """Create a new transform under the given parent. Useful for running into Prims"""
    dag_mod = om.MDagModifier()
    transform_obj = dag_mod.createNode("transform", parent)
    dag_mod.renameNode(transform_obj, name)
    dag_mod.doIt()
    return transform_obj
    
def get_up_axis():
    return cmds.upAxis(query=True, axis=True).upper()
    
def get_node_type(node):
    if cmds.nodeType(node) == 'transform':
        children = cmds.listRelatives(node, children=True, shapes=True, fullPath=True)
        if children:
            return cmds.nodeType(children[0])
    return cmds.nodeType(node)