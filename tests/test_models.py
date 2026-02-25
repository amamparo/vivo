from server.models import AbletonState
from tests.factories import make_track


class TestAbletonState:
    def test_get_group_tracks_returns_only_foldable_tracks(self):
        state = AbletonState()
        state.tracks = {
            0: make_track(0, name="Aaron's Mix", is_group=True),
            1: make_track(1, name="Drums", group_track_index=0, is_grouped=True),
            2: make_track(2, name="Sarah's Mix", is_group=True),
        }
        groups = state.get_group_tracks()
        assert len(groups) == 2
        assert {g.name for g in groups} == {"Aaron's Mix", "Sarah's Mix"}

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
