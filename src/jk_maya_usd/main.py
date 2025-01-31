''' Custom USD Workflow '''

from maya import cmds

from pxr import Usd, UsdGeom

from jk_maya_usd.constants import DEFAULT_CAMERAS, DESTINATION
from jk_maya_usd.prims import prim_classes

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
            
            print(f"Prim created: {prim.GetName()}")
            
    def export(self, top_dag_node: str = ""):
        
        self.stage = Usd.Stage.CreateNew(DESTINATION) # TODO: Should come dynamically from somewhere
        
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
                for child in cmds.listRelatives(node, children=True, fullPath=True):
                    dfs.append((child, target))
        self.stage.GetRootLayer().Save()

class CustomUSDImporter():
    def __init__(self, file: str):
        self.file = file