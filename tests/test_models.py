from server.models import AbletonState
from tests.factories import make_track


class TestGetMixTracks:
    def test_groups_with_non_group_children_are_mixes(self):
        state = AbletonState()
        state.tracks = {
            0: make_track(0, name="Aaron's Mix", is_group=True),
            1: make_track(1, name="Drums", group_track_index=0, is_grouped=True),
            2: make_track(2, name="Sarah's Mix", is_group=True),
            3: make_track(3, name="Bass", group_track_index=2, is_grouped=True),
        }
        mixes = state.get_mix_tracks()
        assert len(mixes) == 2
        assert {m.name for m in mixes} == {"Aaron's Mix", "Sarah's Mix"}

    def test_group_with_only_group_children_is_not_a_mix(self):
        state = AbletonState()
        state.tracks = {
            0: make_track(0, name="Monitor", is_group=True),
            1: make_track(1, name="Aaron's Mix", is_group=True, group_track_index=0, is_grouped=True),
            2: make_track(2, name="Drums", group_track_index=1, is_grouped=True),
            3: make_track(3, name="Bass", group_track_index=1, is_grouped=True),
        }
        mixes = state.get_mix_tracks()
        assert len(mixes) == 1
        assert mixes[0].name == "Aaron's Mix"

    def test_nested_mixes_inside_organizational_group(self):
        state = AbletonState()
        state.tracks = {
            0: make_track(0, name="Monitor", is_group=True),
            1: make_track(1, name="Aaron's Mix", is_group=True, group_track_index=0, is_grouped=True),
            2: make_track(2, name="Drums", group_track_index=1, is_grouped=True),
            3: make_track(3, name="Bass", group_track_index=1, is_grouped=True),
            4: make_track(4, name="Sarah's Mix", is_group=True, group_track_index=0, is_grouped=True),
            5: make_track(5, name="Drums", group_track_index=4, is_grouped=True),
            6: make_track(6, name="Keys", group_track_index=4, is_grouped=True),
        }
        mixes = state.get_mix_tracks()
        assert {m.name for m in mixes} == {"Aaron's Mix", "Sarah's Mix"}

    def test_empty_group_is_not_a_mix(self):
        state = AbletonState()
        state.tracks = {
            0: make_track(0, name="Empty Group", is_group=True),
        }
        assert state.get_mix_tracks() == []

    def test_get_children_returns_tracks_belonging_to_group(self):
        state = AbletonState()
        state.tracks = {
            0: make_track(0, name="Mix A", is_group=True),
            1: make_track(1, name="Drums", group_track_index=0),
            2: make_track(2, name="Bass", group_track_index=0),
            3: make_track(3, name="Mix B", is_group=True),
            4: make_track(4, name="Guitar", group_track_index=3),
        }
        children = state.get_children(0)
        assert [c.name for c in children] == ["Drums", "Bass"]

    def test_get_children_excludes_tracks_from_other_groups(self):
        state = AbletonState()
        state.tracks = {
            0: make_track(0, is_group=True),
            1: make_track(1, name="Drums", group_track_index=0),
            5: make_track(5, is_group=True),
            6: make_track(6, name="Keys", group_track_index=5),
        }
        assert [c.name for c in state.get_children(0)] == ["Drums"]
        assert [c.name for c in state.get_children(5)] == ["Keys"]

    def test_get_children_returns_sorted_by_index(self):
        state = AbletonState()
        state.tracks = {
            0: make_track(0, is_group=True),
            5: make_track(5, group_track_index=0),
            3: make_track(3, group_track_index=0),
            1: make_track(1, group_track_index=0),
        }
        children = state.get_children(0)
        assert [c.index for c in children] == [1, 3, 5]

    def test_get_children_returns_empty_when_group_has_no_children(self):
        state = AbletonState()
        state.tracks = {0: make_track(0, is_group=True)}
        assert state.get_children(0) == []
