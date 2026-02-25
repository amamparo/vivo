import asyncio
import threading
from abc import ABC, abstractmethod

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from server.models import AbletonState, Track


class AbletonBridge(ABC):
    @abstractmethod
    def set_volume(self, track_index: int, volume: float) -> None: ...

    @abstractmethod
    def set_mute(self, track_index: int, mute: bool) -> None: ...

    @abstractmethod
    def start_listeners(self, track_indices: list[int]) -> None: ...

    @abstractmethod
    def stop_all_listeners(self) -> None: ...

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def refresh_tracks(self) -> None:
        pass


class AbletonOSCBridge(AbletonBridge):
    def __init__(self, state: AbletonState) -> None:
        self._state = state
        self._client = SimpleUDPClient("127.0.0.1", 11000)
        self._listen_port = 11001
        self._listeners_started: set[tuple[str, int]] = set()
        self._server: BlockingOSCUDPServer | None = None
        self._server_thread: threading.Thread | None = None
        self._pending: dict[str, asyncio.Future] = {}
        self._loop: asyncio.AbstractEventLoop | None = None

    async def startup(self) -> None:
        self._loop = asyncio.get_event_loop()

        dispatcher = Dispatcher()
        dispatcher.map("/live/song/get/num_tracks", self._handle_num_tracks)
        dispatcher.map("/live/song/get/track_data", self._handle_track_data)
        dispatcher.map("/live/track/get/volume", self._handle_volume)
        dispatcher.map("/live/track/get/mute", self._handle_mute)
        dispatcher.map("/live/track/get/output_meter_left", self._handle_meter_left)
        dispatcher.map("/live/track/get/output_meter_right", self._handle_meter_right)

        self._server = BlockingOSCUDPServer(("0.0.0.0", self._listen_port), dispatcher)
        self._server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._server_thread.start()

        await self.refresh_tracks()

    async def shutdown(self) -> None:
        self.stop_all_listeners()
        if self._server:
            self._server.shutdown()

    def _send(self, address: str, *args) -> None:
        self._client.send_message(address, list(args))

    async def _query(self, address: str, *args, timeout: float = 2.0):
        future = self._loop.create_future()
        self._pending[address] = future
        self._send(address, *args)
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            self._pending.pop(address, None)
            return None

    def _resolve_pending(self, address: str, value) -> None:
        future = self._pending.pop(address, None)
        if future and not future.done():
            self._loop.call_soon_threadsafe(future.set_result, value)

    async def refresh_tracks(self) -> None:
        result = await self._query("/live/song/get/num_tracks")
        if result is None:
            return
        num_tracks = result

        self._send(
            "/live/song/get/track_data",
            0, num_tracks,
            "track.name", "track.color", "track.is_foldable",
            "track.is_grouped", "track.group_track", "track.mute",
        )
        data = await self._query("/live/song/get/track_data", timeout=5.0)
        if data is None:
            return

        props_per_track = 6
        old_tracks = self._state.tracks
        self._state.tracks = {}

        for i in range(num_tracks):
            offset = i * props_per_track
            if offset + props_per_track > len(data):
                break

            name = data[offset]
            color = data[offset + 1]
            is_foldable = bool(data[offset + 2])
            is_grouped = bool(data[offset + 3])
            group_track_raw = data[offset + 4]
            mute = bool(data[offset + 5])

            group_track_index = (
                int(group_track_raw)
                if group_track_raw is not None and str(group_track_raw) != "None"
                else -1
            )

            old = old_tracks.get(i)
            self._state.tracks[i] = Track(
                index=i,
                name=str(name),
                color=int(color) if color is not None else 0,
                is_group=is_foldable,
                is_grouped=is_grouped,
                group_track_index=group_track_index,
                volume=old.volume if old else 0.85,
                mute=mute,
                meter_left=old.meter_left if old else 0.0,
                meter_right=old.meter_right if old else 0.0,
            )

        for i in range(num_tracks):
            self._send("/live/track/get/volume", i)

    def set_volume(self, track_index: int, volume: float) -> None:
        self._send("/live/track/set/volume", track_index, volume)

    def set_mute(self, track_index: int, mute: bool) -> None:
        self._send("/live/track/set/mute", track_index, int(mute))

    def start_listeners(self, track_indices: list[int]) -> None:
        for idx in track_indices:
            for prop in ("volume", "mute", "output_meter_left", "output_meter_right"):
                key = (prop, idx)
                if key not in self._listeners_started:
                    self._send(f"/live/track/start_listen/{prop}", idx)
                    self._listeners_started.add(key)

    def stop_all_listeners(self) -> None:
        for prop, idx in self._listeners_started:
            self._send(f"/live/track/stop_listen/{prop}", idx)
        self._listeners_started.clear()

    def _handle_num_tracks(self, address, *args) -> None:
        if args:
            self._resolve_pending("/live/song/get/num_tracks", args[0])

    def _handle_track_data(self, address, *args) -> None:
        self._resolve_pending("/live/song/get/track_data", args)

    def _handle_volume(self, address, *args) -> None:
        if len(args) >= 2:
            idx, vol = int(args[0]), float(args[1])
            track = self._state.tracks.get(idx)
            if track:
                track.volume = vol

    def _handle_mute(self, address, *args) -> None:
        if len(args) >= 2:
            idx, mute = int(args[0]), bool(args[1])
            track = self._state.tracks.get(idx)
            if track:
                track.mute = mute

    def _handle_meter_left(self, address, *args) -> None:
        if len(args) >= 2:
            idx, level = int(args[0]), float(args[1])
            track = self._state.tracks.get(idx)
            if track:
                track.meter_left = level

    def _handle_meter_right(self, address, *args) -> None:
        if len(args) >= 2:
            idx, level = int(args[0]), float(args[1])
            track = self._state.tracks.get(idx)
            if track:
                track.meter_right = level
