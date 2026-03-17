import atexit
import os
from pathlib import Path

import injector

from server.app import create_app
from server.bridge import AbletonBridge, AbletonOSCBridge
from server.models import AbletonState
from server.solo_manager import SoloManager

PID_FILE = Path(__file__).resolve().parent.parent / "logs" / "live-ears.pid"


def _write_pid():
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))


def _remove_pid():
    PID_FILE.unlink(missing_ok=True)


_write_pid()
atexit.register(_remove_pid)


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
