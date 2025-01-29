from abc import ABC, abstractmethod

from maya import cmds

class PrimBase(ABC):
    @abstractmethod
    def export_node(self, stage, dag_node):
        pass

    @abstractmethod
    def import_prim(self, stage, usd_prim):
        pass

class Xform(PrimBase):
    def export_node(self, stage, dag_node):
        return "Xform"
    
    def import_prim(self, stage, usd_prim):
        pass

class Mesh(PrimBase):
    def export_node(self, stage, dag_node):
        return "Mesh"
    
    def import_prim(self, stage, usd_prim):
        pass
    
    
prim_classes = {
    'transform': Xform,
    'xform': Xform,
    'mesh': Mesh,
}