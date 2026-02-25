import injector

from server.bridge import AbletonBridge
from server.models import AbletonState
from server.solo_manager import SoloManager


class MixerService:
    @injector.inject
    def __init__(self, state: AbletonState, solo_mgr: SoloManager, bridge: AbletonBridge) -> None:
        self.state = state
        self.solo_mgr = solo_mgr
        self.bridge = bridge

    @staticmethod
    def ableton_color_to_hex(color_int: int) -> str:
        if not color_int:
            return "#555555"
        r = (color_int >> 16) & 0xFF
        g = (color_int >> 8) & 0xFF
        b = color_int & 0xFF
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_mixes(self) -> dict:
        groups = self.state.get_mix_tracks()
        mixes = []
        for g in groups:
            children = self.state.get_children(g.index)
            mixes.append({
                "index": g.index,
                "name": g.name,
                "color": self.ableton_color_to_hex(g.color),
                "track_count": len(children),
            })
        return {"type": "mixes", "mixes": mixes}

    def get_mix_state(self, group_index: int) -> dict:
        group = self.state.tracks.get(group_index)
        if not group:
            return {"type": "mix_state", "group_index": group_index, "master": None, "tracks": []}

        children = self.state.get_children(group_index)
        soloed = self.solo_mgr.get_soloed(group_index)

        tracks = []
        for c in children:
            tracks.append({
                "index": c.index,
                "name": c.name,
                "color": self.ableton_color_to_hex(c.color),
                "volume": c.volume,
                "mute": c.mute,
                "solo": c.index in soloed,
                "meter_left": c.meter_left,
                "meter_right": c.meter_right,
            })

        return {
            "type": "mix_state",
            "group_index": group_index,
            "master": {
                "index": group.index,
                "name": group.name,
                "volume": group.volume,
                "mute": group.mute,
                "meter_left": group.meter_left,
                "meter_right": group.meter_right,
            },
            "tracks": tracks,
        }

    def get_meters(self, group_index: int) -> dict:
        group = self.state.tracks.get(group_index)
        children = self.state.get_children(group_index)

        levels = {}
        if group:
            levels[group.index] = {"left": group.meter_left, "right": group.meter_right}
        for c in children:
            levels[c.index] = {"left": c.meter_left, "right": c.meter_right}

        return {"type": "meters", "levels": levels}

    def set_volume(self, track_index: int, volume: float) -> None:
        self.bridge.set_volume(track_index, volume)
        track = self.state.tracks.get(track_index)
        if track:
            track.volume = volume

    def set_mute(self, track_index: int, mute: bool) -> None:
        self.bridge.set_mute(track_index, mute)
        track = self.state.tracks.get(track_index)
        if track:
            track.mute = mute

    def toggle_solo(self, group_index: int, track_index: int) -> dict:
        children = self.state.get_children(group_index)
        child_indices = [c.index for c in children]
        current_mutes = {c.index: c.mute for c in children}

        mute_commands = self.solo_mgr.toggle_solo(
            group_index, track_index, child_indices, current_mutes
        )

        for idx, mute_val in mute_commands.items():
            self.bridge.set_mute(idx, mute_val)
            track = self.state.tracks.get(idx)
            if track:
                track.mute = mute_val

        return self.get_mix_state(group_index)
