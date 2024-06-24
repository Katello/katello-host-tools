def find_module(module_name):
    try:
        import importlib
        module_spec = importlib.util.find_spec(module_name)
        if module_spec is None:
            raise ImportError("Module not found: {}".format(module_name))
        return module_spec
    except (ImportError, AttributeError):
        import imp
        return imp.find_module(module_name)
