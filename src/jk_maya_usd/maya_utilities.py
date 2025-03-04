
from maya import cmds

def get_scene_scale():
    meters_per_unit = cmds.currentUnit(query=True, linear=True)
    return {
        "mm": 0.001,
        "cm": 0.01,  
        "m": 1.0,
        "in": 0.0254,
        "ft": 0.3048,
        "yd": 0.9144,
    }.get(meters_per_unit, 1.0)
    
    
def get_up_axis():
    return cmds.upAxis(query=True, axis=True).upper()
    