""" Helper functions for working with Maya """

from maya import cmds
from maya.api import OpenMaya as om

from jk_maya_usd.constants import CALLBACK_ID_LONGNAME, CALLBACK_ID_SHORTNAME, USD_Kind, USD_Purpose, USD_Type, COLORS

def get_scene_scale() -> float:
    """
    Returns the scene scale in meters based on current linear unit.

    Returns:
        float: Scene scale in meters.
    """
    meters_per_unit = cmds.currentUnit(query=True, linear=True)
    return {
        "mm": 0.001,
        "cm": 0.01,
        "m": 1.0,
        "in": 0.0254,
        "ft": 0.3048,
        "yd": 0.9144,
    }.get(meters_per_unit, 1.0)



def get_mesh_fn_from_dag(dag_node: str) -> om.MFnMesh:
    """
    Returns an MFnMesh function set from the given DAG node name.

    Args:
        dag_node (str): Name of the DAG node.

    Returns:
        om.MFnMesh: The mesh function set for the node.
    """
    selection_list = om.MSelectionList()
    selection_list.add(dag_node)
    dag_path = selection_list.getDagPath(0)
    return om.MFnMesh(dag_path)



def get_mobject_from_name(name: str) -> om.MObject:
    """
    Returns the MObject of the given node name.

    Args:
        name (str): Node name.

    Returns:
        om.MObject: The corresponding MObject.
    """
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
    
def get_up_axis() -> str:
    """
    Returns the current up axis in Maya (e.g., 'Y' or 'Z').

    Returns:
        str: The up axis in uppercase.
    """
    return cmds.upAxis(query=True, axis=True).upper()
    
def get_node_type(node: str) -> str:
    """
    Returns type type of the node.
    Args:
        node (str): The name of the node.

    Returns:
        str: The determined node type.
    """    
    if cmds.nodeType(node) == 'transform':
        children = cmds.listRelatives(node, children=True, shapes=True, fullPath=True)
        if children:
            return cmds.nodeType(children[0])

        if cmds.attributeQuery("type", node=node, exists=True):
            index = cmds.getAttr(f"{node}.type")
            return list(USD_Type)[index].value

    return cmds.nodeType(node)

def set_outliner_color(node: str, rgb: tuple[float, float, float]):
    """
    Sets the outliner color of a node.

    Args:
        node (str): The name of the node.
        rgb (tuple[float, float, float]): RGB values for the color.
    """
    r, g, b = rgb
    cmds.setAttr(f"{node}.useOutlinerColor", 1)
    cmds.setAttr(f"{node}.outlinerColor", r, g, b, type="float3")


def create_group(name: str, parent: str | None = None) -> str:
    """
    Creates an empty group with the specified name in Maya.

    Args:
        name (str): Name of the group to create.
        parent (str | None, optional): Parent node to group under. Defaults to None.

    Returns:
        str: The name of the created group.
    """
    if parent and cmds.objExists(parent):
        group = cmds.group(empty=True, name=name, parent=parent)
    else:
        group = cmds.group(empty=True, name=name)
    return group

def create_scope(name: str, parent: str) -> str:
    """
    Creates a group with a 'Scope' type attribute.

    Args:
        name (str): Name of the group to create.
        parent (str): Parent node to group under.

    Returns:
        str: The name of the created scope group.
    """
    group = create_group(name, parent)
    scope = add_type_attribute(group, "Scope")
    return scope

def create_variant(name: str, parent: str) -> str:
    """
    Creates a group with a 'Variant' type attribute.

    Args:
        name (str): Name of the group to create.
        parent (str): Parent node to group under.

    Returns:
        str: The name of the created variant group.
    """
    group = create_group(name, parent)
    variant = add_type_attribute(group, "Variant")
    return variant

def create_variant_set(name: str, parent: str) -> str:
    """
    Creates a group with a 'VariantSet' type attribute.

    Args:
        name (str): Name of the group to create.
        parent (str): Parent node to group under.

    Returns:
        str: The name of the created variant set group.
    """
    group = create_group(name, parent)
    variant = add_type_attribute(group, "VariantSet")
    return variant

def on_type_change(
    msg: int,
    plug: om.MPlug,
    other_plug: om.MPlug,
    data: any):
    """
    Callback triggered when 'type' attribute changes. Updates outliner color.

    Args:
        msg (int): Message type.
        plug (om.MPlug): Changed plug.
        other_plug (om.MPlug): Related plug.
        data (any): User data.
    """
    attr_name = plug.partialName()
    if attr_name != "type":
        return

    enum_index = plug.asShort()
    node = plug.name().split('.')[0]
    set_outliner_color(node, COLORS[enum_index])
    cmds.select(node)
    
def get_dagpath_from_uuid(uuid: str) -> om.MDagPath:
    """
    Returns the MDagPath of a node from its UUID.

    Args:
        uuid (str): The UUID of the node.

    Returns:
        om.MDagPath: The DAG path of the node.
    """
    node = cmds.ls(str(uuid), uuid=True)
    if not node:
        raise RuntimeError(f"No node found for UUID: {uuid}")
    sel = om.MSelectionList()
    sel.add(node[0])
    return sel.getDagPath(0)


def add_purpose_attribute(node: str, value: str, lock: bool = False) -> str:
    """
    Adds a 'purpose' enum attribute to the node and sets its value.

    Args:
        node (str): The name of the node.
        value (str): The enum value to assign (render, guide, proxy, or default).
        lock (bool, optional): Whether to lock the attribute. Defaults to False.

    Returns:
        str: The modified node.
    """
    attribute_name = "purpose"

    if not cmds.attributeQuery(attribute_name, node=node, exists=True):
        enum_names = ":".join(e.value for e in USD_Purpose)
        cmds.addAttr(node, longName=attribute_name, attributeType="enum", enumName=enum_names)

    enum_value = next(i for i, e in enumerate(USD_Purpose) if e.value == value)
    cmds.setAttr(f"{node}.{attribute_name}", enum_value, lock=lock)
    return node

def add_type_attribute(node: str, value: str, lock: bool = False) -> str:
    """
    Adds a USD type attribute to the node.
    Args:
        node (str): The name of the node.
        value (str): The enum value to assign (Xform, Variant, VariantSet, Scope).
        lock (bool, optional): Whether to lock the attribute. Defaults to False.

    Returns:
        str: The modified node.
    """
    if not cmds.attributeQuery("type", node=node, exists=True):
        enum_names = ":".join(e.value for e in USD_Type)
        cmds.addAttr(node, longName="type", attributeType="enum", enumName=enum_names)
    
    enum_value = next(i for i, e in enumerate(USD_Type) if e.value == value)
    set_outliner_color(node, COLORS[enum_value])
    cmds.setAttr(f"{node}.type", enum_value, lock=lock)
    
    if not cmds.attributeQuery(CALLBACK_ID_LONGNAME, node=node, exists=True):
        selection_list = om.MSelectionList()
        selection_list.add(node)
        m_node = selection_list.getDependNode(0)
        callback_id = om.MNodeMessage.addAttributeChangedCallback(m_node, on_type_change)
        cmds.addAttr(node, longName=CALLBACK_ID_LONGNAME, shortName=CALLBACK_ID_SHORTNAME, attributeType="long")
        cmds.setAttr(f"{node}.{CALLBACK_ID_SHORTNAME}", callback_id, lock=True)
    return node