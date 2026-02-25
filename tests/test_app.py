from starlette.testclient import TestClient

from server.models import AbletonState
from server.bridge import AbletonBridge
from tests.factories import make_track


class TestWebSocket:
    def test_receives_available_mixes_on_connect(self, app, state):
        state.tracks = {
            0: make_track(0, name="My Mix", is_group=True),
            1: make_track(1, name="Drums", group_track_index=0),
        }
        client = TestClient(app)
        with client.websocket_connect("/ws") as ws:
            data = ws.receive_json()
            assert data["type"] == "mixes"
            assert data["mixes"][0]["name"] == "My Mix"
            assert data["mixes"][0]["track_count"] == 1

    def test_select_mix_returns_mix_state_with_group_as_master(self, app, state):
        state.tracks = {
            0: make_track(0, name="Aaron's Mix", is_group=True, volume=0.75),
            1: make_track(1, name="Drums", group_track_index=0),
            2: make_track(2, name="Bass", group_track_index=0),
        }
        client = TestClient(app)
        with client.websocket_connect("/ws") as ws:
            ws.receive_json()
            ws.send_json({"type": "select_mix", "group_index": 0})
            data = ws.receive_json()
            assert data["type"] == "mix_state"
            assert data["master"]["name"] == "Aaron's Mix"
            assert data["master"]["volume"] == 0.75
            assert len(data["tracks"]) == 2

    def test_set_volume_updates_track_state(self, app, state, bridge):
        state.tracks = {
            0: make_track(0, is_group=True),
            1: make_track(1, group_track_index=0, volume=0.5),
        }
        client = TestClient(app)
        with client.websocket_connect("/ws") as ws:
            ws.receive_json()
            ws.send_json({"type": "set_volume", "track_index": 1, "volume": 0.8})
        assert state.tracks[1].volume == 0.8
        assert (1, 0.8) in bridge.volume_commands

    def test_toggle_solo_returns_updated_mix_state(self, app, state):
        state.tracks = {
            0: make_track(0, is_group=True),
            1: make_track(1, group_track_index=0),
            2: make_track(2, group_track_index=0),
        }
        client = TestClient(app)
        with client.websocket_connect("/ws") as ws:
            ws.receive_json()
            ws.send_json({"type": "select_mix", "group_index": 0})
            ws.receive_json()
            ws.send_json({"type": "toggle_solo", "track_index": 1})
            data = ws.receive_json()
            assert data["type"] == "mix_state"
            soloed = [t for t in data["tracks"] if t["solo"]]
            assert len(soloed) == 1
            assert soloed[0]["index"] == 1
            non_soloed = [t for t in data["tracks"] if not t["solo"]]
            assert all(t["mute"] for t in non_soloed)

    def test_set_mute_updates_track_state(self, app, state, bridge):
        state.tracks = {
            0: make_track(0, is_group=True),
            1: make_track(1, group_track_index=0, mute=False),
        }
        client = TestClient(app)
        with client.websocket_connect("/ws") as ws:
            ws.receive_json()
            ws.send_json({"type": "set_mute", "track_index": 1, "mute": True})
        assert state.tracks[1].mute is True
        assert (1, True) in bridge.mute_commands
