__version__ = "0.1.0-dev+18a9a0"

from .vivosc import VivOSC

def create_instance(c_instance):
    return VivOSC(c_instance)
