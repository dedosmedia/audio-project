from intercom.receiver.audio.gst_pipeline import GstAudioPipeline
from intercom.shared.service import Service


class Receiver(Service):
    """High-level receiver abstraction; the long-running component
    exposed to main.py, REST layers, etc.
    """

    def __init__(self, pipeline: GstAudioPipeline) -> None:
        super().__init__()
        self._pipeline = pipeline
        self._muted = False
        self._pre_mute_volume = pipeline.get_volume()

    def _do_start(self) -> None:
        self._pipeline.start()

    def _do_stop(self) -> None:
        self._pipeline.stop()

    @property
    def volume(self) -> float:
        return self._pipeline.get_volume()

    @volume.setter
    def volume(self, value: float) -> None:
        self._muted = False
        self._pipeline.set_volume(value)

    @property
    def is_muted(self) -> bool:
        return self._muted

    def mute(self) -> None:
        if self._muted:
            return
        self._pre_mute_volume = self._pipeline.get_volume()
        self._pipeline.set_volume(0.0)
        self._muted = True

    def unmute(self) -> None:
        if not self._muted:
            return
        self._pipeline.set_volume(self._pre_mute_volume)
        self._muted = False

    def toggle_mute(self) -> None:
        self.unmute() if self._muted else self.mute()
