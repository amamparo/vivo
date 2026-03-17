__version__ = "0.1.0+7588b7"

from .liveearsosc import LiveEarsOSC

def create_instance(c_instance):
    return LiveEarsOSC(c_instance)
