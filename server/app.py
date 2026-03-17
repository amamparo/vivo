import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import injector
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from server.bridge import AbletonBridge
from server.mixer_service import MixerService

logger = logging.getLogger("live-ears")

UI_DIST = Path(__file__).resolve().parent.parent / "ui" / "dist"
METER_INTERVAL = 0.05
TRACK_POLL_INTERVAL = 5.0


def create_app(container: injector.Injector) -> FastAPI:
    mixer = container.get(MixerService)
    bridge = container.get(AbletonBridge)
    client_mix_groups: dict[WebSocket, int | None] = {}

    async def meter_loop():
        while True:
            await asyncio.sleep(METER_INTERVAL)
            if not client_mix_groups:
                continue
            for ws, group_index in list(client_mix_groups.items()):
                if group_index is not None:
                    try:
                        await ws.send_text(json.dumps(mixer.get_meters(group_index)))
                    except Exception:
                        pass

    async def track_poll_loop():
        while True:
            await asyncio.sleep(TRACK_POLL_INTERVAL)
            try:
                await bridge.refresh_tracks()
                bridge.start_listeners(list(mixer.state.tracks.keys()))
                mixes_data = json.dumps(mixer.get_mixes())
                for ws, group_index in list(client_mix_groups.items()):
                    try:
                        await ws.send_text(mixes_data)
                        if group_index is not None:
                            state = mixer.get_mix_state(group_index)
                            if not state["master"]:
                                client_mix_groups[ws] = None
                            await ws.send_text(json.dumps(state))
                    except Exception:
                        pass
            except Exception:
                logger.exception("Error polling tracks")

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        await bridge.startup()
        bridge.start_listeners(list(mixer.state.tracks.keys()))

        meter_task = asyncio.create_task(meter_loop())
        poll_task = asyncio.create_task(track_poll_loop())

        yield

        meter_task.cancel()
        poll_task.cancel()
        await bridge.shutdown()

    app = FastAPI(lifespan=lifespan)

    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        await ws.accept()
        client_mix_groups[ws] = None

        try:
            await ws.send_text(json.dumps(mixer.get_mixes()))

            while True:
                raw = await ws.receive_text()
                msg = json.loads(raw)
                msg_type = msg.get("type")

                if msg_type == "select_mix":
                    group_index = msg["group_index"]
                    client_mix_groups[ws] = group_index
                    children = mixer.state.get_children(group_index)
                    bridge.start_listeners([group_index] + [c.index for c in children])
                    await ws.send_text(json.dumps(mixer.get_mix_state(group_index)))

                elif msg_type == "set_volume":
                    mixer.set_volume(msg["track_index"], float(msg["volume"]))

                elif msg_type == "set_mute":
                    mixer.set_mute(msg["track_index"], bool(msg["mute"]))

                elif msg_type == "toggle_solo":
                    group_index = client_mix_groups.get(ws)
                    if group_index is not None:
                        result = mixer.toggle_solo(group_index, msg["track_index"])
                        await ws.send_text(json.dumps(result))

                elif msg_type == "request_mix_state":
                    group_index = client_mix_groups.get(ws)
                    if group_index is not None:
                        await ws.send_text(json.dumps(mixer.get_mix_state(group_index)))

        except WebSocketDisconnect:
            pass
        except Exception:
            logger.exception("WebSocket error")
        finally:
            client_mix_groups.pop(ws, None)

    if UI_DIST.exists():
        app.mount("/", StaticFiles(directory=str(UI_DIST), html=True), name="ui")

    return app
