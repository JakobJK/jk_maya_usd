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

from jk_maya_usd.constants import USD_Kind, USD_Purpose, USD_Type

CALLBACK_ID_LONGNAME = "callbackId"
CALLBACK_ID_SHORTNAME = "cbid"

USD_ATTRIBUTE_KEY = "composer-attributes"

usd_attributes = {'type': USD_Type, 'kind': USD_Kind, 'purpose': USD_Purpose}
bool_attributes = {"default_variant"}


colors = {
    "variant_set": (0.8, 0.2, 1.0),
    "variant": (1, 0.5, 1.0),
    "scope": (0.0, 1.0, 1.0),
    "xform": (1, 1, 1)
}


def set_outline_color(node, rgb):
    cmds.undoInfo(openChunk=True)
    r, g, b = rgb
    cmds.setAttr(f"{node}.useOutlinerColor", 1)
    cmds.setAttr(f'{node}.outlinerColor', r, g, b, 'float3')

    # We need to select the node for the outliner to update
    selection = cmds.ls(selection=True)
    cmds.select(clear=True)
    cmds.select(node)
    cmds.select(selection, clear=True)
    cmds.undoInfo(closeChunk=True)



def on_type_change(msg, plug, other_plug, data):
    attr_name = plug.partialName()

    if plug.isNull:
        return

    if msg & om.MNodeMessage.kAttributeAdded:
        return

    if not (msg & om.MNodeMessage.kAttributeSet):
        return

    if attr_name != "type":
        return
    
    enum_index = plug.asShort()
    enum_value = list(USD_Type)[enum_index]
    print(enum_value)


def set_default_variant(node, type, value):
    """Sets the current node variant as the default variant for the variant set
    """
    pass

def add_type_attribute(node, usd_type, value, lock=False):
    if not cmds.attributeQuery(usd_type, node=node, exists=True):
        enum_names = ":".join(e.value for e in usd_attributes[usd_type])
        cmds.addAttr(node, longName=usd_type, attributeType="enum", enumName=enum_names)

    enum_value = next(i for i, e in enumerate(usd_attributes[usd_type]) if e.value == value)
    cmds.setAttr(f"{node}.{usd_type}", enum_value, lock=lock)
    
    if not cmds.attributeQuery(CALLBACK_ID_LONGNAME, node=node, exists=True):
        selection_list = om.MSelectionList()
        selection_list.add(node)
        m_node = selection_list.getDependNode(0)
        callback_id = om.MNodeMessage.addAttributeChangedCallback(m_node, on_type_change)

        cmds.addAttr(node, longName=CALLBACK_ID_LONGNAME, shortName=CALLBACK_ID_SHORTNAME, attributeType="long")
        cmds.setAttr(f"{node}.{CALLBACK_ID_SHORTNAME}", callback_id, lock=True)


def add_purpose_attribute(node, value, lock=False):
    attribute_name = "purpose"

    if not cmds.attributeQuery(attribute_name, node=node, exists=True):
        enum_names = ":".join(e.value for e in USD_Purpose)
        cmds.addAttr(node, longName=attribute_name, attributeType="enum", enumName=enum_names)

    enum_value = next(i for i, e in enumerate(USD_Purpose) if e.value == value)
    cmds.setAttr(f"{node}.{attribute}", enum_value, lock=lock)