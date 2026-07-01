from intercom.sender.audio.gst_pipeline import GstAudioPipeline
from intercom.shared.service import Service


class Sender(Service):
    """High-level sender abstraction; the long-running component
    exposed to main.py.
    """

    def __init__(self, pipeline: GstAudioPipeline) -> None:
        super().__init__()
        self._pipeline = pipeline

    def _do_start(self) -> None:
        self._pipeline.start()

    def _do_stop(self) -> None:
        self._pipeline.stop()
