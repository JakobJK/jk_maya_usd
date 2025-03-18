from jk_maya_usd.prims.primbase import PrimBase

from pxr import UsdGeom, Vt, Sdf
from maya.api import OpenMaya as om

class Mesh(PrimBase):
    def _export_impl(self, stage, dag_node, target):
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

    def get_mobject_from_name(self, name):
        """Get MObject from a node name."""
        sel = om.MSelectionList()
        sel.add(name)
        return sel.getDependNode(0)

    def create_transform(self, name, parent):
        """Create a new transform under the given parent."""
        dag_mod = om.MDagModifier()
        transform_obj = dag_mod.createNode("transform", parent)
        dag_mod.renameNode(transform_obj, name)
        dag_mod.doIt()
        return transform_obj

    def _import_impl(self, stage, usd_prim, parent):
        if not usd_prim or not usd_prim.IsValid():
            return None

        mesh = UsdGeom.Mesh(usd_prim)

        points_attr = mesh.GetPointsAttr()
        points = points_attr.Get() or []

        mfloat_points = om.MFloatPointArray()
        for x, y, z in points:
            mfloat_points.append(om.MFloatPoint(x, y, z))

        face_vertex_indices = mesh.GetFaceVertexIndicesAttr().Get() or []
        face_vertex_indices = om.MIntArray(face_vertex_indices)

        face_vertex_counts = mesh.GetFaceVertexCountsAttr().Get() or []
        face_vertex_counts = om.MIntArray(face_vertex_counts)

        if len(mfloat_points) == 0 or len(face_vertex_counts) == 0:
            return None

        parent_obj = self.get_mobject_from_name(parent)

        transform_name = usd_prim.GetName()
        transform_obj = self.create_transform(transform_name, parent_obj)

        mesh_fn = om.MFnMesh()
        mesh_obj = mesh_fn.create(
            mfloat_points, 
            face_vertex_counts,
            face_vertex_indices,
            parent=transform_obj
        )

        dag_path = om.MDagPath.getAPathTo(mesh_obj)
        transform_fn = om.MFnDagNode(dag_path)
        shape_obj = dag_path.node()
        shading_group = om.MSelectionList().add("initialShadingGroup").getDependNode(0)
        om.MFnSet(shading_group).addMember(shape_obj)

        return dag_path.fullPathName()
