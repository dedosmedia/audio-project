import gi

gi.require_version("Gst", "1.0")

from gi.repository import Gst


class GstAudioPipeline:
    """
    GStreamer-based RTP/Opus audio receiver pipeline.
    """

    def __init__(self, config):

        Gst.init(None)

        self.config = config
        self.pipeline = None
        self.volume = None

        self._build_pipeline()

    def _build_pipeline(self):

        pipeline_str = f"""
        udpsrc port={self.config.udp_port}
        caps="application/x-rtp,payload=96,encoding-name=OPUS,clock-rate=48000"
        !
        rtpjitterbuffer latency={self.config.latency_ms}
        !
        rtpopusdepay
        !
        opusdec
        !
        audioconvert
        !
        audioresample
        !
        volume name=volume volume={self.config.default_volume}
        !
        alsasink device={self.config.audio_device}
        """

        self.pipeline = Gst.parse_launch(pipeline_str)

        self.volume = self.pipeline.get_by_name("volume")

        if self.volume is None:
            raise RuntimeError("Failed to locate volume element in pipeline")

    def start(self):

        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):

        self.pipeline.set_state(Gst.State.NULL)

    def set_volume(self, value: float):

        value = max(0.0, min(2.0, value))
        self.volume.set_property("volume", value)

    def get_volume(self) -> float:

        return float(self.volume.get_property("volume"))