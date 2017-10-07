import importlib
import pkgutil
from commitizen.cz.cz_angular import AngularCz


registry = {
    name: importlib.import_module(name).__all__[0]
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('cz_')
}

registry.update({
    'cz_angular': AngularCz
})
