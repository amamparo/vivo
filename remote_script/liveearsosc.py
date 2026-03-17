"""
LiveEarsOSC — minimal Ableton Remote Script for Live Ears.

Exposes only the OSC addresses that Live Ears uses: track metadata queries,
volume/mute get/set, and listeners for volume/mute/meters.
"""

from ableton.v2.control_surface import ControlSurface
import Live

from .osc_server import OSCServer, OSC_LISTEN_PORT

import logging
import os

logger = logging.getLogger("liveearsosc")


class LiveEarsOSC(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)

        self._track_listeners = {}
        self._mixer_listeners = {}
        self._log_handler = None

        self._init_logging()

        try:
            self._osc = OSCServer()
        except OSError as e:
            self.show_message("LiveEarsOSC: Couldn't bind to port %d (%s)" % (OSC_LISTEN_PORT, e))
            logger.error("Couldn't bind to port %d (%s)" % (OSC_LISTEN_PORT, e))
            return

        self._init_osc_handlers()
        self.schedule_message(0, self._tick)
        self.show_message("LiveEarsOSC: Listening on port %d" % OSC_LISTEN_PORT)
        logger.info("Started LiveEarsOSC on port %d" % OSC_LISTEN_PORT)

    # ── OSC handlers ──────────────────────────────────────────────────

    def _init_osc_handlers(self):
        self._osc.add_handler("/live/song/get/num_tracks", self._on_get_num_tracks)
        self._osc.add_handler("/live/song/get/track_data", self._on_get_track_data)

        for prop in ("mute", "output_meter_left", "output_meter_right"):
            self._osc.add_handler("/live/track/get/%s" % prop, self._make_track_getter(prop))
            self._osc.add_handler("/live/track/start_listen/%s" % prop, self._make_track_listen_start(prop))
            self._osc.add_handler("/live/track/stop_listen/%s" % prop, self._make_track_listen_stop(prop))

        self._osc.add_handler("/live/track/set/mute", self._on_set_mute)

        self._osc.add_handler("/live/track/get/volume", self._on_get_volume)
        self._osc.add_handler("/live/track/set/volume", self._on_set_volume)
        self._osc.add_handler("/live/track/start_listen/volume", self._on_start_listen_volume)
        self._osc.add_handler("/live/track/stop_listen/volume", self._on_stop_listen_volume)

    # ── Song ──────────────────────────────────────────────────────────

    def _on_get_num_tracks(self, params):
        return (len(self.song.tracks),)

    def _on_get_track_data(self, params):
        track_index_min, track_index_max, *properties = params
        track_index_min = int(track_index_min)
        track_index_max = int(track_index_max)
        tracks = self.song.tracks
        if track_index_max == -1:
            track_index_max = len(tracks)
        rv = []
        for i in range(track_index_min, track_index_max):
            track = tracks[i]
            for prop in properties:
                obj, attr = prop.split(".")
                if obj == "track":
                    value = getattr(track, attr)
                    if isinstance(value, Live.Track.Track):
                        value = list(tracks).index(value)
                    rv.append(value)
        return tuple(rv)

    # ── Track: mute and meters (direct track properties) ─────────────

    def _make_track_getter(self, prop):
        def callback(params):
            track_index = int(params[0])
            track = self.song.tracks[track_index]
            value = getattr(track, prop)
            return (track_index, value)
        return callback

    def _on_set_mute(self, params):
        track_index = int(params[0])
        self.song.tracks[track_index].mute = params[1]

    def _make_track_listen_start(self, prop):
        def callback(params):
            track_index = int(params[0])
            track = self.song.tracks[track_index]
            key = (prop, track_index)

            if key in self._track_listeners:
                self._remove_track_listener(key)

            def on_change():
                value = getattr(track, prop)
                self._osc.send("/live/track/get/%s" % prop, (track_index, value))

            getattr(track, "add_%s_listener" % prop)(on_change)
            self._track_listeners[key] = (track, on_change)
            on_change()
        return callback

    def _make_track_listen_stop(self, prop):
        def callback(params):
            track_index = int(params[0])
            self._remove_track_listener((prop, track_index))
        return callback

    def _remove_track_listener(self, key):
        if key not in self._track_listeners:
            return
        prop, _ = key
        track, fn = self._track_listeners.pop(key)
        try:
            getattr(track, "remove_%s_listener" % prop)(fn)
        except Exception as e:
            logger.info("Exception removing track listener (likely benign): %s" % e)

    # ── Track: volume (mixer_device property) ─────────────────────────

    def _on_get_volume(self, params):
        track_index = int(params[0])
        return (track_index, self.song.tracks[track_index].mixer_device.volume.value)

    def _on_set_volume(self, params):
        track_index = int(params[0])
        self.song.tracks[track_index].mixer_device.volume.value = params[1]

    def _on_start_listen_volume(self, params):
        track_index = int(params[0])
        parameter = self.song.tracks[track_index].mixer_device.volume
        key = ("volume", track_index)

        if key in self._mixer_listeners:
            self._remove_mixer_listener(key)

        def on_change():
            self._osc.send("/live/track/get/volume", (track_index, parameter.value))

        parameter.add_value_listener(on_change)
        self._mixer_listeners[key] = (parameter, on_change)
        on_change()

    def _on_stop_listen_volume(self, params):
        track_index = int(params[0])
        self._remove_mixer_listener(("volume", track_index))

    def _remove_mixer_listener(self, key):
        if key not in self._mixer_listeners:
            return
        parameter, fn = self._mixer_listeners.pop(key)
        try:
            parameter.remove_value_listener(fn)
        except Exception as e:
            logger.info("Exception removing mixer listener (likely benign): %s" % e)

    # ── Lifecycle ─────────────────────────────────────────────────────

    def _tick(self):
        self._osc.process()
        self.schedule_message(1, self._tick)

    def disconnect(self):
        for key in list(self._track_listeners):
            self._remove_track_listener(key)
        for key in list(self._mixer_listeners):
            self._remove_mixer_listener(key)
        if hasattr(self, "_osc"):
            self._osc.shutdown()
        if self._log_handler:
            logger.removeHandler(self._log_handler)
        super().disconnect()

    def _init_logging(self):
        try:
            from ._config import LOG_DIR
            log_dir = LOG_DIR
        except ImportError:
            log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logs")
        if not os.path.exists(log_dir):
            os.mkdir(log_dir, 0o755)
        self._log_handler = logging.FileHandler(os.path.join(log_dir, "liveearsosc.log"))
        self._log_handler.setLevel(logging.INFO)
        self._log_handler.setFormatter(logging.Formatter("(%(asctime)s) [%(levelname)s] %(message)s"))
        logger.addHandler(self._log_handler)
