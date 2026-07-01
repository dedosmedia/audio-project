import gi

gi.require_version("Gst", "1.0")

from gi.repository import Gst


class ReceiverPipeline:

    def __init__(
        self,
        port: int,
        device: str,
        volume: float,
        latency: int,
    ):

        Gst.init(None)

        self.pipeline = Gst.parse_launch(
            f"""
            udpsrc port={port}
            caps="application/x-rtp,payload=96,encoding-name=OPUS,clock-rate=48000"
            !
            rtpjitterbuffer latency={latency}
            !
            rtpopusdepay
            !
            opusdec
            !
            audioconvert
            !
            audioresample
            !
            volume name=volume volume={volume}
            !
            alsasink device={device}
            """
        )

        self.volume = self.pipeline.get_by_name("volume")

    def start(self):
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)

    def set_volume(self, value: float):
        self.volume.set_property("volume", value)

    def get_volume(self):

        return self.volume.get_property("volume")