from server.bridge import AbletonBridge
from server.models import Track


class InMemoryBridge(AbletonBridge):
    def __init__(self) -> None:
        self.volume_commands: list[tuple[int, float]] = []
        self.mute_commands: list[tuple[int, bool]] = []

    def set_volume(self, track_index: int, volume: float) -> None:
        self.volume_commands.append((track_index, volume))

    def set_mute(self, track_index: int, mute: bool) -> None:
        self.mute_commands.append((track_index, mute))

    def start_listeners(self, track_indices: list[int]) -> None:
        pass

    def stop_all_listeners(self) -> None:
        pass


def make_track(index: int, **kwargs) -> Track:
    defaults = dict(
        name="",
        color=0,
        is_group=False,
        is_grouped=False,
        group_track_index=-1,
        volume=0.85,
        mute=False,
        meter_left=0.0,
        meter_right=0.0,
    )
    defaults.update(kwargs)
    return Track(index=index, **defaults)
