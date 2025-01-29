# jk_maya_usd


```python
import sys
import importlib
import pkgutil

def recursive_reload(module):
    importlib.reload(module)

    # Walk through all submodules and reload them
    for submodule in pkgutil.walk_packages(module.__path__, module.__name__ + "."):
        submod = importlib.import_module(submodule.name)
        importlib.reload(submod)

# Path to your package
p = '/Users/jakobkousholt/repos/jk_maya_usd/src'

if p not in sys.path:
    sys.path.append(p)

import jk_maya_usd
recursive_reload(jk_maya_usd)

print(jk_maya_usd)

```
