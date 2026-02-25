from dataclasses import dataclass, field


@dataclass
class _GroupSoloState:
    soloed: set[int] = field(default_factory=set)
    pre_solo_mutes: dict[int, bool] = field(default_factory=dict)


class SoloManager:
    def __init__(self) -> None:
        self._groups: dict[int, _GroupSoloState] = {}

    def get_soloed(self, group_index: int) -> set[int]:
        state = self._groups.get(group_index)
        return state.soloed.copy() if state else set()

    def toggle_solo(
        self,
        group_index: int,
        track_index: int,
        child_indices: list[int],
        current_mutes: dict[int, bool],
    ) -> dict[int, bool]:
        if group_index not in self._groups:
            self._groups[group_index] = _GroupSoloState()

        state = self._groups[group_index]
        mute_commands: dict[int, bool] = {}

        if track_index in state.soloed:
            state.soloed.discard(track_index)

            if not state.soloed:
                for idx in child_indices:
                    mute_commands[idx] = state.pre_solo_mutes.get(idx, False)
                state.pre_solo_mutes.clear()
            else:
                mute_commands[track_index] = True
        else:
            if not state.soloed:
                for idx in child_indices:
                    state.pre_solo_mutes[idx] = current_mutes.get(idx, False)

            state.soloed.add(track_index)

            for idx in child_indices:
                mute_commands[idx] = idx not in state.soloed

        return mute_commands
