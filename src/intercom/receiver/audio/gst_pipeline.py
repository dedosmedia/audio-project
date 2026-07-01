"""RTP/Opus audio receiver pipeline built manually with GStreamer.

Elements are created individually (instead of Gst.parse_launch) and kept
as instance variables so callers can control volume, reconnect, or add
diagnostics later without re-parsing the pipeline description.
"""

import gi

gi.require_version("Gst", "1.0")

from gi.repository import Gst

from intercom.shared.config import ReceiverConfig
from intercom.shared.constants import (
    MAX_VOLUME,
    MIN_VOLUME,
    RTP_CLOCK_RATE_HZ,
    RTP_ENCODING_NAME,
    RTP_PAYLOAD_TYPE_OPUS,
)
from intercom.shared.exceptions import PipelineError
from intercom.shared.logger import logger


class GstAudioPipeline:
    """Manually constructed GStreamer pipeline: RTP/Opus in, ALSA out."""

    def __init__(self, config: ReceiverConfig) -> None:
        Gst.init(None)

        self._config = config

        self._pipeline: Gst.Pipeline
        self._udpsrc: Gst.Element
        self._jitterbuffer: Gst.Element
        self._rtpdepay: Gst.Element
        self._opusdec: Gst.Element
        self._audioconvert: Gst.Element
        self._audioresample: Gst.Element
        self._volume: Gst.Element
        self._alsasink: Gst.Element
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
        self._pipeline = Gst.Pipeline.new("receiver-pipeline")

        self._udpsrc = self._make_element("udpsrc", "udpsrc")
        self._udpsrc.set_property("port", self._config.udp_port)
        self._udpsrc.set_property(
            "caps",
            Gst.Caps.from_string(
                "application/x-rtp,"
                f"payload={RTP_PAYLOAD_TYPE_OPUS},"
                f"encoding-name={RTP_ENCODING_NAME},"
                f"clock-rate={RTP_CLOCK_RATE_HZ}"
            ),
        )

        self._jitterbuffer = self._make_element("rtpjitterbuffer", "jitterbuffer")
        self._jitterbuffer.set_property("latency", self._config.latency_ms)

        self._rtpdepay = self._make_element("rtpopusdepay", "rtpdepay")
        self._opusdec = self._make_element("opusdec", "opusdec")
        self._audioconvert = self._make_element("audioconvert", "audioconvert")
        self._audioresample = self._make_element("audioresample", "audioresample")

        self._volume = self._make_element("volume", "volume")
        self._volume.set_property("volume", self._config.default_volume)

        self._alsasink = self._make_element("alsasink", "alsasink")
        self._alsasink.set_property("device", self._config.audio_device)

        for element in (
            self._udpsrc,
            self._jitterbuffer,
            self._rtpdepay,
            self._opusdec,
            self._audioconvert,
            self._audioresample,
            self._volume,
            self._alsasink,
        ):
            self._pipeline.add(element)

        self._link(self._udpsrc, self._jitterbuffer)
        self._link(self._jitterbuffer, self._rtpdepay)
        self._link(self._rtpdepay, self._opusdec)
        self._link(self._opusdec, self._audioconvert)
        self._link(self._audioconvert, self._audioresample)
        self._link(self._audioresample, self._volume)
        self._link(self._volume, self._alsasink)

        self._bus = self._pipeline.get_bus()
        self._bus.add_signal_watch()
        self._bus.connect("message", self._on_bus_message)

    def _on_bus_message(self, bus: Gst.Bus, message: Gst.Message) -> None:
        if message.type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            logger.error("Receiver pipeline error: %s (%s)", error, debug)
        elif message.type == Gst.MessageType.WARNING:
            warning, debug = message.parse_warning()
            logger.warning("Receiver pipeline warning: %s (%s)", warning, debug)
        elif message.type == Gst.MessageType.EOS:
            logger.info("Receiver pipeline reached end-of-stream")
        elif message.type == Gst.MessageType.STATE_CHANGED and message.src == self._pipeline:
            old_state, new_state, _pending = message.parse_state_changed()
            logger.info(
                "Receiver pipeline state changed: %s -> %s",
                old_state.value_nick,
                new_state.value_nick,
            )

    def start(self) -> None:
        self._pipeline.set_state(Gst.State.PLAYING)

    def stop(self) -> None:
        self._pipeline.set_state(Gst.State.NULL)

    def set_volume(self, value: float) -> None:
        value = max(MIN_VOLUME, min(MAX_VOLUME, value))
        self._volume.set_property("volume", value)

    def get_volume(self) -> float:
        return float(self._volume.get_property("volume"))
