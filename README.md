# jk_maya_usd

 This is an attempt at making a custom USD import/exporter. I am a simple dude, with simple and specific needs. My goal is a simple workflow, that is easy to test!

```python
import sys
import importlib
import pkgutil

def recursive_reload(module):
    importlib.reload(module)
    for submodule in pkgutil.walk_packages(module.__path__, module.__name__ + "."):
        submod = importlib.import_module(submodule.name)
        importlib.reload(submod)

# Path to your package
p = '/Users/jakobkousholt/repos/jk_maya_usd/src'

if p not in sys.path:
    sys.path.append(p)

import jk_maya_usd
recursive_reload(jk_maya_usd)

d = jk_maya_usd.main.CustomUSDExporter()
d.export()
```