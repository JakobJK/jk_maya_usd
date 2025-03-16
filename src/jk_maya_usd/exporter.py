''' Custom USD Workflow '''

from maya import cmds
from pxr import Usd, UsdGeom

from jk_maya_usd.constants import DEFAULT_CAMERAS, DESTINATION
from jk_maya_usd.prims import prim_classes

from jk_maya_usd.maya_utilities import get_scene_scale, get_up_axis

def get_node_type(node):
    if cmds.nodeType(node) == 'transform':
        children = cmds.listRelatives(node, children=True, shapes=True, fullPath=True)
        if children:
            return cmds.nodeType(children[0])
    return cmds.nodeType(node)

class CustomUSDExporter():
    def __init__(self):
        self.stage = ""
    
    def process(self, dag_node, node_type, target):
        if node_type in prim_classes:
            cls = prim_classes[node_type]() 
            prim = cls.export_node(self.stage, dag_node, target)
            print(f"Prim({prim.GetTypeName()}) created: {prim.GetName()}")
            
            
    def _create_stage(self, destination):
        self.stage = Usd.Stage.CreateNew(destination)
        
        up_axis = get_up_axis()
        meters_per_unit = get_scene_scale()
        
        up_axis_token = UsdGeom.Tokens.y if up_axis == 'Y' else UsdGeom.Tokens.z
        
        UsdGeom.SetStageUpAxis(self.stage, up_axis_token)
        UsdGeom.SetStageMetersPerUnit(self.stage, meters_per_unit) 
            
    def export(self, top_dag_node: str = ""):
        self._create_stage(DESTINATION)
                
        if top_dag_node:
            dag_nodes = [node for node in cmds.listRelatives(top_dag_node,children=True, type="transform", fullPath=True)]
        else:            
            dag_nodes = [node for node in cmds.ls(type="transform", long=True) 
                if not cmds.listRelatives(node, parent=True)
                and node not in DEFAULT_CAMERAS]
        
        ROOT = ""
        
        dfs = [(node, ROOT) for node in dag_nodes]
        
        while dfs:
            node, parent = dfs.pop()
            node_type = get_node_type(node)
            short_name = node.split('|')[-1]
            target = f"{parent}/{short_name}"
            self.process(node, node_type, target)
            if node_type == 'transform':
                if children := cmds.listRelatives(node, children=True, fullPath=True):
                    for child in children:
                        dfs.append((child, target))
        self.stage.GetRootLayer().Save()
