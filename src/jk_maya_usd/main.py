''' Custom USD Workflow '''

from maya import cmds

from pxr import Usd, UsdGeom

from jk_maya_usd.constants import DEFAULT_CAMERAS

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
    
    def process(self, node, node_type, parent):
        if node_type in prim_classes:
            cls = prim_classes[node_type]() 
            prim = cls.export_node(self.stage, node)
            
            print(prim)
            
            # self.stage.addPrim(prim)
        
    def export(self):
        ROOT = "/"
        
        dag_nodes = [
            (node, ROOT) for node in cmds.ls(type="transform", long=True) 
            if not cmds.listRelatives(node, parent=True)
            and node not in DEFAULT_CAMERAS
            ]
        
        while dag_nodes:
            node, parent = dag_nodes.pop()
            node_type = get_node_type(node)
            
            self.process(node, node_type, parent)
            
            if node_type == 'transform':
                short_name = cmds.ls(node, shortNames=True)[0]
                for child in cmds.listRelatives(node, children=True, fullPath=True):
                    dag_nodes.append((child, parent + short_name))


class CustomUSDImporter():
    def __init__(self, file: str):
        self.file = file