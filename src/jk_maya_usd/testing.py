from pxr import Usd

def compare_usd_stages(generated_stage_path: str, target_stage_path: str) -> dict:
    """Compares two USD stages from file paths and returns a detailed diff report."""
    
    generated_stage = Usd.Stage.Open(generated_stage_path)
    target_stage = Usd.Stage.Open(target_stage_path)

    report = {
        "prims_only_in_generated": [],
        "prims_only_in_target": [],
        "attribute_differences": {}
    }

    generated_prims = {prim.GetPath(): prim for prim in generated_stage.Traverse()}
    target_prims = {prim.GetPath(): prim for prim in target_stage.Traverse()}

    generated_paths = set(generated_prims.keys())
    target_paths = set(target_prims.keys())

    report["prims_only_in_generated"] = list(generated_paths - target_paths)
    report["prims_only_in_target"] = list(target_paths - generated_paths)

    common_prims = generated_paths & target_paths

    for path in common_prims:
        gen_prim = generated_prims[path]
        tgt_prim = target_prims[path]

        gen_attrs = {attr.GetName(): attr.Get() for attr in gen_prim.GetAttributes()}
        tgt_attrs = {attr.GetName(): attr.Get() for attr in tgt_prim.GetAttributes()}

        attr_diffs = {}

        for attr in set(gen_attrs.keys()).union(tgt_attrs.keys()):
            if attr not in tgt_attrs:
                attr_diffs[attr] = {"status": "missing_in_target", "generated_value": gen_attrs[attr]}
            elif attr not in gen_attrs:
                attr_diffs[attr] = {"status": "missing_in_generated", "target_value": tgt_attrs[attr]}
            elif gen_attrs[attr] != tgt_attrs[attr]:
                attr_diffs[attr] = {"status": "value_mismatch", "generated_value": gen_attrs[attr], "target_value": tgt_attrs[attr]}

        if attr_diffs:
            report["attribute_differences"][str(path)] = attr_diffs

    return report
