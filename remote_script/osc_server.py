"""
Non-blocking UDP server for OSC message dispatch.

pythonosc's built-in server beachballs in Ableton's single-threaded runtime,
so this uses a raw non-blocking socket polled from the ControlSurface tick loop.
"""

from .pythonosc.osc_message import OscMessage, ParseError
from .pythonosc.osc_bundle import OscBundle
from .pythonosc.osc_message_builder import OscMessageBuilder, BuildError

import errno
import socket
import logging
import traceback

OSC_LISTEN_PORT = 11000
OSC_RESPONSE_PORT = 11001

logger = logging.getLogger("vivosc")


class OSCServer:
    def __init__(self):
        self._remote_addr = ('127.0.0.1', OSC_RESPONSE_PORT)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setblocking(False)
        self._socket.bind(('0.0.0.0', OSC_LISTEN_PORT))
        self._callbacks = {}

    def add_handler(self, address, callback):
        self._callbacks[address] = callback

    def send(self, address, params=()):
        msg_builder = OscMessageBuilder(address)
        for param in params:
            msg_builder.add_arg(param)
        try:
            self._socket.sendto(msg_builder.build().dgram, self._remote_addr)
        except BuildError:
            logger.error("OSC build error: %s" % traceback.format_exc())

    def process(self):
        try:
            while True:
                data, remote_addr = self._socket.recvfrom(65536)
                self._remote_addr = (remote_addr[0], OSC_RESPONSE_PORT)
                self._parse(data, remote_addr)
        except socket.error as e:
            if e.errno == errno.ECONNRESET:
                logger.warning("Non-fatal socket error: %s" % traceback.format_exc())
            elif e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                logger.error("Socket error: %s" % traceback.format_exc())
        except Exception as e:
            logger.error("Error handling OSC message: %s" % e)

    def shutdown(self):
        self._socket.close()

    def _parse(self, data, remote_addr):
        try:
            if OscBundle.dgram_is_bundle(data):
                self._handle_bundle(OscBundle(data), remote_addr)
            else:
                self._handle_message(OscMessage(data), remote_addr)
        except ParseError:
            logger.error("OSC parse error: %s" % traceback.format_exc())

    def _handle_bundle(self, bundle, remote_addr):
        for item in bundle:
            if OscBundle.dgram_is_bundle(item.dgram):
                self._handle_bundle(item, remote_addr)
            else:
                self._handle_message(item, remote_addr)

    def _handle_message(self, message, remote_addr):
        callback = self._callbacks.get(message.address)
        if not callback:
            return
        rv = callback(message.params)
        if rv is not None:
            response_addr = (remote_addr[0], OSC_RESPONSE_PORT)
            msg_builder = OscMessageBuilder(message.address)
            for param in rv:
                msg_builder.add_arg(param)
            try:
                self._socket.sendto(msg_builder.build().dgram, response_addr)
            except BuildError:
                logger.error("OSC build error: %s" % traceback.format_exc())
