import importlib
import pkgutil
from commitizen.cz.cz_angular import AngularCz


registry = {
    name: importlib.import_module(name).discover_this
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('cz_')
}

registry.update({
    'cz_angular': AngularCz
})
