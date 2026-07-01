"""Bridges a browser microphone into the receiver's own RTP/Opus/UDP input.

The browser captures raw PCM16 and streams it over a WebSocket; each
session builds a short-lived GStreamer pipeline (appsrc -> opusenc ->
rtpopuspay -> udpsink) that talks to the receiver on localhost exactly
like any other sender. The receiver itself never learns this exists.
"""

import gi

gi.require_version("Gst", "1.0")

from gi.repository import Gst
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from intercom.shared.constants import AUDIO_CHANNELS, OPUS_BITRATE_BPS, RTP_CLOCK_RATE_HZ, RTP_PAYLOAD_TYPE_OPUS
from intercom.shared.exceptions import PipelineError
from intercom.shared.logger import logger

router = APIRouter()


class WebMicPipeline:
    """Manually constructed GStreamer pipeline: appsrc in, RTP/Opus out."""

    def __init__(self, udp_port: int, source_sample_rate: int) -> None:
        Gst.init(None)

        self._udp_port = udp_port
        self._source_sample_rate = source_sample_rate

        self._pipeline: Gst.Pipeline
        self._appsrc: Gst.Element

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
        self._pipeline = Gst.Pipeline.new("web-mic-pipeline")

        self._appsrc = self._make_element("appsrc", "appsrc")
        self._appsrc.set_property(
            "caps",
            Gst.Caps.from_string(
                "audio/x-raw,format=S16LE,layout=interleaved,"
                f"rate={self._source_sample_rate},channels={AUDIO_CHANNELS}"
            ),
        )
        self._appsrc.set_property("format", Gst.Format.TIME)
        self._appsrc.set_property("is-live", True)
        self._appsrc.set_property("do-timestamp", True)
        self._appsrc.set_property("block", True)

        audioconvert = self._make_element("audioconvert", "audioconvert")
        audioresample = self._make_element("audioresample", "audioresample")

        capsfilter = self._make_element("capsfilter", "capsfilter")
        capsfilter.set_property(
            "caps",
            Gst.Caps.from_string(
                f"audio/x-raw,rate={RTP_CLOCK_RATE_HZ},channels={AUDIO_CHANNELS}"
            ),
        )

        opusenc = self._make_element("opusenc", "opusenc")
        opusenc.set_property("bitrate", OPUS_BITRATE_BPS)

        rtppay = self._make_element("rtpopuspay", "rtppay")
        rtppay.set_property("pt", RTP_PAYLOAD_TYPE_OPUS)

        udpsink = self._make_element("udpsink", "udpsink")
        udpsink.set_property("host", "127.0.0.1")
        udpsink.set_property("port", self._udp_port)

        for element in (
            self._appsrc,
            audioconvert,
            audioresample,
            capsfilter,
            opusenc,
            rtppay,
            udpsink,
        ):
            self._pipeline.add(element)

        self._link(self._appsrc, audioconvert)
        self._link(audioconvert, audioresample)
        self._link(audioresample, capsfilter)
        self._link(capsfilter, opusenc)
        self._link(opusenc, rtppay)
        self._link(rtppay, udpsink)

        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_bus_message)

    def _on_bus_message(self, bus: Gst.Bus, message: Gst.Message) -> None:
        if message.type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            logger.error("Web mic pipeline error: %s (%s)", error, debug)
        elif message.type == Gst.MessageType.WARNING:
            warning, debug = message.parse_warning()
            logger.warning("Web mic pipeline warning: %s (%s)", warning, debug)

    def start(self) -> None:
        self._pipeline.set_state(Gst.State.PLAYING)

    def stop(self) -> None:
        self._appsrc.emit("end-of-stream")
        self._pipeline.set_state(Gst.State.NULL)

    def push_pcm(self, data: bytes) -> None:
        self._appsrc.emit("push-buffer", Gst.Buffer.new_wrapped(data))


@router.websocket("/ws/talk")
async def talk(websocket: WebSocket) -> None:
    await websocket.accept()

    receiver_config = websocket.app.state.receiver_config
    sample_rate = int(websocket.query_params.get("sample_rate", RTP_CLOCK_RATE_HZ))

    pipeline = WebMicPipeline(udp_port=receiver_config.udp_port, source_sample_rate=sample_rate)
    pipeline.start()
    logger.info("Web mic session started at %d Hz", sample_rate)

    try:
        while True:
            data = await websocket.receive_bytes()
            pipeline.push_pcm(data)
    except WebSocketDisconnect:
        pass
    finally:
        pipeline.stop()
        logger.info("Web mic session ended")
