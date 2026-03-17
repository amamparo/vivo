__version__ = "0.1.0+a71e2e"

from .vivosc import VivOSC

def create_instance(c_instance):
    return VivOSC(c_instance)
