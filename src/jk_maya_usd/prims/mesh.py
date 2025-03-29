from jk_maya_usd.prims.primbase import PrimBase
from jk_maya_usd.maya_utilities import create_transform, get_mobject_from_name, get_dagpath_from_uuid, get_mesh_fn_from_dag
from pxr import UsdGeom, Vt, Sdf
from maya.api import OpenMaya as om

class Mesh(PrimBase):
    def _export_bounding_box(self, mesh_fn, prim):
        bbox = mesh_fn.boundingBox
        min_pt, max_pt = bbox.min, bbox.max
        extent = Vt.Vec3fArray([(min_pt.x, min_pt.y, min_pt.z), (max_pt.x, max_pt.y, max_pt.z)])
        UsdGeom.Boundable(prim).CreateExtentAttr().Set(extent)

    def _export_mesh_data(self, mesh_fn, mesh, prim):
        points = mesh_fn.getPoints(om.MSpace.kWorld)
        mesh.GetPointsAttr().Set(Vt.Vec3fArray([(p.x, p.y, p.z) for p in points]))
        face_counts = []
        face_connects = []
        uv_indices = []

        uv_set_name = mesh_fn.currentUVSetName()
        u_array, v_array = mesh_fn.getUVs(uv_set_name)

        if not u_array or not v_array:
            return prim

        st_array = Vt.Vec2fArray(list(zip(u_array, v_array)))

        for i in range(mesh_fn.numPolygons):
            vtx_ids = mesh_fn.getPolygonVertices(i)
            face_counts.append(len(vtx_ids))
            face_connects.extend(vtx_ids)
            for j in range(len(vtx_ids)):
                uv_id = mesh_fn.getPolygonUVid(i, j, uv_set_name)
                uv_indices.append(uv_id)

        mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray(face_counts))
        mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray(face_connects))
        st_primvar = UsdGeom.PrimvarsAPI(prim).CreatePrimvar(
            "st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying
        )
        st_primvar.Set(st_array)
        st_primvar.SetIndices(Vt.IntArray(uv_indices))

    def _export_impl(self, stage, dag_node, target):
        mesh = UsdGeom.Mesh.Define(stage, target)
        prim = mesh.GetPrim()

        # Setting points
        mesh_fn = get_mesh_fn_from_dag(dag_node)

        self._export_mesh_data(mesh_fn, mesh, prim)                   
        self._export_displayColor(mesh_fn, mesh, prim)
        self._export_bounding_box(mesh_fn, prim)
        mesh.GetSubdivisionSchemeAttr().Set(UsdGeom.Tokens.catmullClark) 
        return prim

    def _import_impl(self, stage, usd_prim, parent):
        if not usd_prim or not usd_prim.IsValid():
            return None

        mesh = UsdGeom.Mesh(usd_prim)
        mesh.GetSubdivisionSchemeAttr().Set(UsdGeom.Tokens.catmullClark)

        points = mesh.GetPointsAttr().Get() or []
        face_vertex_indices = mesh.GetFaceVertexIndicesAttr().Get() or []
        face_vertex_counts = mesh.GetFaceVertexCountsAttr().Get() or []

        if not points or not face_vertex_counts:
            return None

        mfloat_points = om.MFloatPointArray([om.MFloatPoint(x, y, z) for x, y, z in points])
        face_vertex_indices = om.MIntArray(face_vertex_indices)
        face_vertex_counts = om.MIntArray(face_vertex_counts)

        mesh_fn = om.MFnMesh()
        mesh_obj = mesh_fn.create(mfloat_points, face_vertex_counts, face_vertex_indices)

        # Cache UUID to recover later
        uuid = om.MFnDependencyNode(mesh_obj).uuid()

        # Get initial shape DAG path
        shape_path = om.MDagPath.getAPathTo(mesh_obj)
        shape_path.extendToShape()
        mesh_fn = om.MFnMesh(shape_path)

        # UVs
        primvars_api = UsdGeom.PrimvarsAPI(mesh.GetPrim())
        st_primvar = primvars_api.GetPrimvar("st")
        if st_primvar and st_primvar.HasValue():
            uv_values = st_primvar.Get()
            uv_indices = st_primvar.GetIndices()
            if uv_values:
                u_array = om.MFloatArray([u for u, _ in uv_values])
                v_array = om.MFloatArray([v for _, v in uv_values])
                mesh_fn.setUVs(u_array, v_array, "map1")

                if uv_indices:
                    uv_ids = om.MIntArray([int(i) for i in uv_indices])
                else:
                    uv_ids = om.MIntArray(range(len(face_vertex_indices)))

                mesh_fn.assignUVs(face_vertex_counts, uv_ids, "map1")

        # Assign shading
        shape_obj = shape_path.node()
        shading_group = om.MSelectionList().add("initialShadingGroup").getDependNode(0)
        om.MFnSet(shading_group).addMember(shape_obj)

        # Parent and freeze
        transform_path = om.MDagPath.getAPathTo(mesh_obj)
        transform_full = transform_path.fullPathName()
        cmds.parent(transform_full, parent)

        # Re-acquire using UUID   
        transform_path = get_dagpath_from_uuid(uuid)

        # Now freeze using fresh path
        cmds.makeIdentity(transform_path.fullPathName(), apply=True, t=1, r=1, s=1, n=0)

        # Reacquire DAG paths from UUID
        shape_path = om.MDagPath(transform_path)
        shape_path.extendToShape()

        # Rename
        transform_name = usd_prim.GetName()
        shape_name = f"{transform_name}Shape"
        om.MFnDependencyNode(transform_path.node()).setName(transform_name)
        om.MFnDependencyNode(shape_path.node()).setName(shape_name)

        return shape_path.fullPathName()

