import injector

from server.app import create_app
from server.bridge import AbletonBridge, AbletonOSCBridge
from server.models import AbletonState
from server.solo_manager import SoloManager


class ProductionModule(injector.Module):
    @injector.singleton
    @injector.provider
    def provide_state(self) -> AbletonState:
        return AbletonState()

    @injector.singleton
    @injector.provider
    def provide_solo_mgr(self) -> SoloManager:
        return SoloManager()

    @injector.singleton
    @injector.provider
    def provide_bridge(self, state: AbletonState) -> AbletonBridge:
        return AbletonOSCBridge(state)


container = injector.Injector([ProductionModule()])
app = create_app(container)
