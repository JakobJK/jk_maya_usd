from jk_maya_usd.prims.primbase import PrimBase

from pxr import Usd, UsdGeom, Vt
from maya.api import OpenMaya as om

class Mesh(PrimBase):
    def export_node(self, stage, dag_node, target):
        mesh = UsdGeom.Mesh.Define(stage, target)
        prim = mesh.GetPrim()  # Extract Usd.Prim for returning

        selection_list = om.MSelectionList()
        selection_list.add(dag_node)
        dag_path = selection_list.getDagPath(0)
        mesh_fn = om.MFnMesh(dag_path)

        points = mesh_fn.getPoints(om.MSpace.kWorld)
        mesh.GetPointsAttr().Set(Vt.Vec3fArray([(p.x, p.y, p.z) for p in points]))

        face_counts = []
        face_connects = []
        for i in range(mesh_fn.numPolygons):
            vertex_indices = mesh_fn.getPolygonVertices(i)
            face_counts.append(len(vertex_indices))
            face_connects.extend(vertex_indices)

        mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray(face_counts))
        mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray(face_connects))
        return prim

    
    def import_prim(self, stage, usd_prim):
        pass