import importlib
import pkgutil

import importlib
import pkgutil
from flask import Blueprint

def register_routes(app):
    package = __name__
    for _, module_name, _ in pkgutil.iter_modules([__path__[0]]):
        module = importlib.import_module(f"{package}.{module_name}")

        # Look for variables ending in `_bp` and being instances of Blueprint
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, Blueprint):
                app.register_blueprint(obj)