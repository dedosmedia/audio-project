from intercom.receiver.audio.gst_pipeline import GstAudioPipeline
from intercom.shared.service import Service


class Receiver(Service):
    """High-level receiver abstraction; the long-running component
    exposed to main.py, REST layers, etc.
    """

    def __init__(self, pipeline: GstAudioPipeline) -> None:
        super().__init__()
        self._pipeline = pipeline

    def _do_start(self) -> None:
        self._pipeline.start()

    def _do_stop(self) -> None:
        self._pipeline.stop()

    @property
    def volume(self) -> float:
        return self._pipeline.get_volume()

    @volume.setter
    def volume(self, value: float) -> None:
        self._pipeline.set_volume(value)
