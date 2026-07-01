"""Microphone capture pipeline built manually with GStreamer.

Captures from PipeWire, encodes to Opus, and streams RTP/UDP to the
receiver. Elements are kept as instance variables so bitrate, target
device, or destination can be controlled dynamically later.
"""

import gi

gi.require_version("Gst", "1.0")

from gi.repository import Gst

from intercom.shared.config import SenderConfig
from intercom.shared.constants import AUDIO_CHANNELS, RTP_CLOCK_RATE_HZ, RTP_PAYLOAD_TYPE_OPUS
from intercom.shared.exceptions import PipelineError
from intercom.shared.logger import logger


class GstAudioPipeline:
    """Manually constructed GStreamer pipeline: mic in, RTP/Opus out."""

    def __init__(self, config: SenderConfig) -> None:
        Gst.init(None)

        self._config = config

        self._pipeline: Gst.Pipeline
        self._pipewiresrc: Gst.Element
        self._audioconvert: Gst.Element
        self._audioresample: Gst.Element
        self._capsfilter: Gst.Element
        self._opusenc: Gst.Element
        self._rtppay: Gst.Element
        self._udpsink: Gst.Element
        self._bus: Gst.Bus

        self._build_pipeline()

    def _make_element(self, factory_name: str, name: str) -> Gst.Element:
        element = Gst.ElementFactory.make(factory_name, name)
        if element is None:
            raise PipelineError(f"Failed to create GStreamer element '{factory_name}'")
        return element

    def _link(self, upstream: Gst.Element, downstream: Gst.Element) -> None:
        if not upstream.link(downstream):
            raise PipelineError(
                f"Failed to link {upstream.get_name()} -> {downstream.get_name()}"
            )

    def _build_pipeline(self) -> None:
        self._pipeline = Gst.Pipeline.new("sender-pipeline")

        self._pipewiresrc = self._make_element("pipewiresrc", "pipewiresrc")
        if self._config.audio_device:
            self._pipewiresrc.set_property("target-object", self._config.audio_device)

        self._audioconvert = self._make_element("audioconvert", "audioconvert")
        self._audioresample = self._make_element("audioresample", "audioresample")

        self._capsfilter = self._make_element("capsfilter", "capsfilter")
        self._capsfilter.set_property(
            "caps",
            Gst.Caps.from_string(
                f"audio/x-raw,rate={RTP_CLOCK_RATE_HZ},channels={AUDIO_CHANNELS}"
            ),
        )

        self._opusenc = self._make_element("opusenc", "opusenc")
        self._opusenc.set_property("bitrate", self._config.bitrate)

        self._rtppay = self._make_element("rtpopuspay", "rtppay")
        self._rtppay.set_property("pt", RTP_PAYLOAD_TYPE_OPUS)

        self._udpsink = self._make_element("udpsink", "udpsink")
        self._udpsink.set_property("host", self._config.receiver_host)
        self._udpsink.set_property("port", self._config.udp_port)

        for element in (
            self._pipewiresrc,
            self._audioconvert,
            self._audioresample,
            self._capsfilter,
            self._opusenc,
            self._rtppay,
            self._udpsink,
        ):
            self._pipeline.add(element)

        self._link(self._pipewiresrc, self._audioconvert)
        self._link(self._audioconvert, self._audioresample)
        self._link(self._audioresample, self._capsfilter)
        self._link(self._capsfilter, self._opusenc)
        self._link(self._opusenc, self._rtppay)
        self._link(self._rtppay, self._udpsink)

        self._bus = self._pipeline.get_bus()
        self._bus.add_signal_watch()
        self._bus.connect("message", self._on_bus_message)

    def _on_bus_message(self, bus: Gst.Bus, message: Gst.Message) -> None:
        if message.type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            logger.error("Sender pipeline error: %s (%s)", error, debug)
        elif message.type == Gst.MessageType.WARNING:
            warning, debug = message.parse_warning()
            logger.warning("Sender pipeline warning: %s (%s)", warning, debug)
        elif message.type == Gst.MessageType.EOS:
            logger.info("Sender pipeline reached end-of-stream")
        elif message.type == Gst.MessageType.STATE_CHANGED and message.src == self._pipeline:
            old_state, new_state, _pending = message.parse_state_changed()
            logger.info(
                "Sender pipeline state changed: %s -> %s",
                old_state.value_nick,
                new_state.value_nick,
            )

    def start(self) -> None:
        self._pipeline.set_state(Gst.State.PLAYING)

    def stop(self) -> None:
        self._pipeline.set_state(Gst.State.NULL)
