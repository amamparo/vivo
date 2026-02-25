from server.solo_manager import SoloManager


class TestSoloManager:
    def setup_method(self):
        self.mgr = SoloManager()
        self.group = 0
        self.children = [1, 2, 3]
        self.all_unmuted = {1: False, 2: False, 3: False}

    def test_soloing_a_track_mutes_all_others(self):
        result = self.mgr.toggle_solo(self.group, 1, self.children, self.all_unmuted)
        assert result == {1: False, 2: True, 3: True}

    def test_soloing_a_second_track_leaves_both_unmuted(self):
        self.mgr.toggle_solo(self.group, 1, self.children, self.all_unmuted)
        result = self.mgr.toggle_solo(self.group, 2, self.children, self.all_unmuted)
        assert result == {1: False, 2: False, 3: True}

    def test_unsoloing_last_track_restores_original_mute_states(self):
        mutes_with_bass_muted = {1: False, 2: True, 3: False}
        self.mgr.toggle_solo(self.group, 1, self.children, mutes_with_bass_muted)
        result = self.mgr.toggle_solo(self.group, 1, self.children, mutes_with_bass_muted)
        assert result == {1: False, 2: True, 3: False}

    def test_unsoloing_one_track_while_another_remains_soloed(self):
        self.mgr.toggle_solo(self.group, 1, self.children, self.all_unmuted)
        self.mgr.toggle_solo(self.group, 2, self.children, self.all_unmuted)
        result = self.mgr.toggle_solo(self.group, 1, self.children, self.all_unmuted)
        assert result == {1: True}

    def test_get_soloed_returns_empty_set_for_unknown_group(self):
        assert self.mgr.get_soloed(999) == set()

    def test_get_soloed_returns_currently_soloed_tracks(self):
        self.mgr.toggle_solo(self.group, 1, self.children, self.all_unmuted)
        self.mgr.toggle_solo(self.group, 2, self.children, self.all_unmuted)
        assert self.mgr.get_soloed(self.group) == {1, 2}

    def test_pre_solo_mute_states_are_only_captured_on_first_solo(self):
        initial_mutes = {1: False, 2: True, 3: False}
        self.mgr.toggle_solo(self.group, 1, self.children, initial_mutes)

        mutes_during_solo = {1: False, 2: True, 3: True}
        self.mgr.toggle_solo(self.group, 3, self.children, mutes_during_solo)

        self.mgr.toggle_solo(self.group, 1, self.children, mutes_during_solo)
        result = self.mgr.toggle_solo(self.group, 3, self.children, mutes_during_solo)
        assert result[2] is True
        assert result[1] is False
        assert result[3] is False

    def test_solo_state_is_isolated_per_group(self):
        self.mgr.toggle_solo(0, 1, [1, 2], {1: False, 2: False})
        self.mgr.toggle_solo(10, 11, [11, 12], {11: False, 12: False})
        assert self.mgr.get_soloed(0) == {1}
        assert self.mgr.get_soloed(10) == {11}
