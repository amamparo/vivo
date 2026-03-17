try:
    from .vivosc import VivOSC
except ImportError:
    pass

def create_instance(c_instance):
    return VivOSC(c_instance)
