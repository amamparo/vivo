import pytest
import injector

from server.app import create_app
from server.bridge import AbletonBridge
from server.models import AbletonState
from server.solo_manager import SoloManager
from tests.factories import InMemoryBridge


class TestModule(injector.Module):
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
    def provide_bridge(self) -> AbletonBridge:
        return InMemoryBridge()


@pytest.fixture
def container():
    return injector.Injector([TestModule()])


@pytest.fixture
def state(container):
    return container.get(AbletonState)


@pytest.fixture
def bridge(container):
    return container.get(AbletonBridge)


@pytest.fixture
def app(container):
    return create_app(container)
