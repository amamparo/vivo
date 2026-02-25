from dataclasses import dataclass, field


@dataclass
class Track:
    index: int
    name: str = ""
    color: int = 0
    is_group: bool = False
    is_grouped: bool = False
    group_track_index: int = -1
    volume: float = 0.85
    mute: bool = False
    meter_left: float = 0.0
    meter_right: float = 0.0


class AbletonState:
    def __init__(self) -> None:
        self.tracks: dict[int, Track] = {}

    def get_group_tracks(self) -> list[Track]:
        return [t for t in self.tracks.values() if t.is_group]

    def get_children(self, group_index: int) -> list[Track]:
        return sorted(
            [t for t in self.tracks.values() if t.group_track_index == group_index],
            key=lambda t: t.index,
        )
