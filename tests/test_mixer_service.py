from server.mixer_service import MixerService
from server.models import AbletonState
from server.solo_manager import SoloManager
from tests.factories import InMemoryBridge, make_track


def create_mixer():
    state = AbletonState()
    solo_mgr = SoloManager()
    bridge = InMemoryBridge()
    return MixerService(state, solo_mgr, bridge), state, bridge


class TestGetMixes:
    def test_returns_group_tracks_as_available_mixes(self):
        mixer, state, _ = create_mixer()
        state.tracks = {
            0: make_track(0, name="Aaron's Mix", is_group=True, color=0xFF0000),
            1: make_track(1, name="Drums", group_track_index=0),
            2: make_track(2, name="Bass", group_track_index=0),
        }
        result = mixer.get_mixes()
        assert result["type"] == "mixes"
        assert len(result["mixes"]) == 1
        assert result["mixes"][0]["track_count"] == 2

    def test_mix_name_is_the_group_track_name(self):
        mixer, state, _ = create_mixer()
        state.tracks = {
            0: make_track(0, name="Sarah's Monitor", is_group=True),
            1: make_track(1, name="Drums", group_track_index=0),
        }
        assert mixer.get_mixes()["mixes"][0]["name"] == "Sarah's Monitor"

    def test_mix_color_is_derived_from_group_track_color(self):
        mixer, state, _ = create_mixer()
        state.tracks = {
            0: make_track(0, is_group=True, color=0xFF8800),
            1: make_track(1, group_track_index=0),
        }
        assert mixer.get_mixes()["mixes"][0]["color"] == "#ff8800"

    def test_organizational_parent_group_is_excluded(self):
        mixer, state, _ = create_mixer()
        state.tracks = {
            0: make_track(0, name="Monitor", is_group=True),
            1: make_track(1, name="Aaron's Mix", is_group=True, group_track_index=0, is_grouped=True),
            2: make_track(2, name="Drums", group_track_index=1, is_grouped=True),
            3: make_track(3, name="Sarah's Mix", is_group=True, group_track_index=0, is_grouped=True),
            4: make_track(4, name="Bass", group_track_index=3, is_grouped=True),
        }
        result = mixer.get_mixes()
        names = [m["name"] for m in result["mixes"]]
        assert "Monitor" not in names
        assert "Aaron's Mix" in names
        assert "Sarah's Mix" in names


class TestGetMixState:
    def test_group_track_fader_serves_as_the_master_output(self):
        mixer, state, _ = create_mixer()
        state.tracks = {
            0: make_track(0, name="My Mix", is_group=True, volume=0.75),
            1: make_track(1, name="Drums", group_track_index=0, volume=0.5),
        }
        result = mixer.get_mix_state(0)
        assert result["master"]["name"] == "My Mix"
        assert result["master"]["volume"] == 0.75
        assert result["master"]["index"] == 0

    def test_child_tracks_appear_as_channel_strips(self):
        mixer, state, _ = create_mixer()
        state.tracks = {
            0: make_track(0, is_group=True),
            1: make_track(1, name="Drums", group_track_index=0),
            2: make_track(2, name="Bass", group_track_index=0),
        }
        result = mixer.get_mix_state(0)
        assert len(result["tracks"]) == 2
        assert result["tracks"][0]["name"] == "Drums"
        assert result["tracks"][1]["name"] == "Bass"

    def test_returns_empty_state_for_nonexistent_group(self):
        mixer, _, _ = create_mixer()
        result = mixer.get_mix_state(999)
        assert result["master"] is None
        assert result["tracks"] == []

    def test_includes_solo_status_from_solo_manager(self):
        mixer, state, _ = create_mixer()
        state.tracks = {
            0: make_track(0, is_group=True),
            1: make_track(1, group_track_index=0),
            2: make_track(2, group_track_index=0),
        }
        mixer.toggle_solo(0, 1)
        result = mixer.get_mix_state(0)
        assert result["tracks"][0]["solo"] is True
        assert result["tracks"][1]["solo"] is False


class TestSetVolume:
    def test_sends_volume_command_to_bridge(self):
        mixer, state, bridge = create_mixer()
        state.tracks = {0: make_track(0, volume=0.5)}
        mixer.set_volume(0, 0.8)
        assert bridge.volume_commands == [(0, 0.8)]

    def test_updates_local_state_immediately(self):
        mixer, state, _ = create_mixer()
        state.tracks = {0: make_track(0, volume=0.5)}
        mixer.set_volume(0, 0.8)
        assert state.tracks[0].volume == 0.8


class TestSetMute:
    def test_sends_mute_command_to_bridge(self):
        mixer, state, bridge = create_mixer()
        state.tracks = {0: make_track(0, mute=False)}
        mixer.set_mute(0, True)
        assert bridge.mute_commands == [(0, True)]

    def test_updates_local_state_immediately(self):
        mixer, state, _ = create_mixer()
        state.tracks = {0: make_track(0, mute=False)}
        mixer.set_mute(0, True)
        assert state.tracks[0].mute is True


class TestToggleSolo:
    def test_mutes_non_soloed_tracks_via_bridge(self):
        mixer, state, bridge = create_mixer()
        state.tracks = {
            0: make_track(0, is_group=True),
            1: make_track(1, group_track_index=0),
            2: make_track(2, group_track_index=0),
            3: make_track(3, group_track_index=0),
        }
        mixer.toggle_solo(0, 1)
        assert (2, True) in bridge.mute_commands
        assert (3, True) in bridge.mute_commands
        assert (1, False) in bridge.mute_commands

    def test_updates_track_mute_states(self):
        mixer, state, _ = create_mixer()
        state.tracks = {
            0: make_track(0, is_group=True),
            1: make_track(1, group_track_index=0),
            2: make_track(2, group_track_index=0),
        }
        mixer.toggle_solo(0, 1)
        assert state.tracks[1].mute is False
        assert state.tracks[2].mute is True

    def test_returns_updated_mix_state(self):
        mixer, state, _ = create_mixer()
        state.tracks = {
            0: make_track(0, is_group=True),
            1: make_track(1, group_track_index=0),
            2: make_track(2, group_track_index=0),
        }
        result = mixer.toggle_solo(0, 1)
        assert result["type"] == "mix_state"
        soloed = [t for t in result["tracks"] if t["solo"]]
        assert len(soloed) == 1
        assert soloed[0]["index"] == 1


class TestGetMeters:
    def test_includes_group_and_child_meter_levels(self):
        mixer, state, _ = create_mixer()
        state.tracks = {
            0: make_track(0, is_group=True),
            1: make_track(1, group_track_index=0),
        }
        state.tracks[0].meter_left = 0.5
        state.tracks[0].meter_right = 0.6
        state.tracks[1].meter_left = 0.3
        state.tracks[1].meter_right = 0.4
        result = mixer.get_meters(0)
        assert result["levels"][0] == {"left": 0.5, "right": 0.6}
        assert result["levels"][1] == {"left": 0.3, "right": 0.4}


class TestColorConversion:
    def test_extracts_rgb_from_ableton_color_integer(self):
        assert MixerService.ableton_color_to_hex(0xFF8800) == "#ff8800"

    def test_returns_default_gray_for_zero(self):
        assert MixerService.ableton_color_to_hex(0) == "#555555"

    def test_handles_low_rgb_values_with_leading_zeros(self):
        assert MixerService.ableton_color_to_hex(0x010203) == "#010203"
