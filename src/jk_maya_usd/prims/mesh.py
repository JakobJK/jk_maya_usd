from jk_maya_usd.prims.primbase import PrimBase

from pxr import Usd, UsdGeom, Vt, Sdf
from maya.api import OpenMaya as om

class Mesh(PrimBase):
    def export_node(self, stage, dag_node, target):
        mesh = UsdGeom.Mesh.Define(stage, target)
        prim = mesh.GetPrim()  

        selection_list = om.MSelectionList()
        selection_list.add(dag_node)
        dag_path = selection_list.getDagPath(0)
        mesh_fn = om.MFnMesh(dag_path)

        points = mesh_fn.getPoints(om.MSpace.kWorld)
        mesh.GetPointsAttr().Set(Vt.Vec3fArray([(p.x, p.y, p.z) for p in points]))

        face_counts = []
        face_connects = []
        uv_indices = []

        uv_set_name = mesh_fn.currentUVSetName()
        u_array, v_array = mesh_fn.getUVs(uv_set_name)
        st_array = Vt.Vec2fArray(list(zip(u_array, v_array)))

        for i in range(mesh_fn.numPolygons):
            vertex_indices = mesh_fn.getPolygonVertices(i)
            face_counts.append(len(vertex_indices))
            face_connects.extend(vertex_indices)

            for j, _ in enumerate(vertex_indices):
                uv_id = mesh_fn.getPolygonUVid(i, j, uv_set_name)
                uv_indices.append(uv_id)

        mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray(face_counts))
        mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray(face_connects))

        st_primvar = UsdGeom.PrimvarsAPI(prim).CreatePrimvar(
            "st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying
        )
        st_primvar.Set(st_array)
        st_primvar.SetIndices(Vt.IntArray(uv_indices))


        return prim

    def import_prim(self, stage, usd_prim):
        pass