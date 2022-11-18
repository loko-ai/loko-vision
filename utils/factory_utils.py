import importlib
import inspect
import pkgutil
from _collections import defaultdict

class BaseFactory:
    def __init__(self, klass="__klass__"):
        self.klass = klass
        self.transformers = {}

    def register(self, name, transformer):
        self.transformers[name] = transformer

    def __call__(self, obj):
        if isinstance(obj, dict):
            if self.klass in obj:
                kl = obj[self.klass]
                args = self({k: self(v) for (k, v) in obj.items() if k != self.klass})
                if isinstance(kl, type) or callable(kl):
                    return kl(**args)
                else:
                    return self.transformers[kl](**args)
            else:
                for k, v in obj.items():
                    return {k: self(v) for (k, v) in obj.items()}
        if isinstance(obj, list):
            return [self(v) for v in obj]

        if isinstance(obj, tuple):
            return (self(v) for v in obj)

        return obj


def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        try:
            package = importlib.import_module(package)
        except:
            print("Err",package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        try:
            full_name = package.__name__ + '.' + name
            results[full_name] = importlib.import_module(full_name)
            if recursive and is_pkg:
                results.update(import_submodules(full_name))
        except:
            pass
    return results

class ClassByNameLoader:
    def __init__(self, base):
        self.base = base
        self.klasses = defaultdict(set)

        for el, m in import_submodules(base).items():
            for name, kl in inspect.getmembers(m, inspect.isclass):
                self.klasses[name].add(kl)

    def find(self, name):
        prefix = None
        if "." in name:
            prefix, name = name.rsplit(".", 1)
        temp = self.klasses.get(name)
        if prefix:
            return {x for x in temp if x.__module__.endswith(prefix)}
        return temp
