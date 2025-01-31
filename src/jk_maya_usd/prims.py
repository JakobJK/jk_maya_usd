from abc import ABC, abstractmethod

from pxr import Usd, UsdGeom, Vt

from maya.api import OpenMaya as om

class PrimBase(ABC):
    @abstractmethod
    def export_node(self, stage: str, dag_node:str, target: str):
        """This will export a node from Maya to the USD stage.

        Args:
            stage (_type_): The current stage we are exporting to.
            dag_node (_type_): The full path of the dag_node from Maya.
            target (_type_): The full path in the usd stage where the prim will be created.

        Returns:
            prim: The newly added prim.
        """
        pass

    @abstractmethod
    def import_prim(self, stage, usd_prim):
        pass


class Mesh(PrimBase):
    def export_node(self, stage, dag_node, target):
        prim = UsdGeom.Mesh.Define(stage, target)

        selection_list = om.MSelectionList()
        selection_list.add(dag_node)
        dag_path = selection_list.getDagPath(0)
        mesh_fn = om.MFnMesh(dag_path)

        points = mesh_fn.getPoints(om.MSpace.kWorld)
        prim.GetPointsAttr().Set(Vt.Vec3fArray([(p.x, p.y, p.z) for p in points]))

        face_counts = []
        face_connects = []
        for i in range(mesh_fn.numPolygons):
            vertex_indices = mesh_fn.getPolygonVertices(i)
            face_counts.append(len(vertex_indices))
            face_connects.extend(vertex_indices)

        prim.GetFaceVertexCountsAttr().Set(Vt.IntArray(face_counts))
        prim.GetFaceVertexIndicesAttr().Set(Vt.IntArray(face_connects))
        return prim

    
    def import_prim(self, stage, usd_prim):
        pass
    
    
class Xform(PrimBase):
    def export_node(self, stage, dag_node, target):
        
        prim = UsdGeom.Xform.Define(stage, target)
        
        return prim
    
    def import_prim(self, stage, usd_prim):
        pass

    
prim_classes = {
    'transform': Xform,
    'xform': Xform,
    'mesh': Mesh,
}