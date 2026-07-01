from intercom_receiver.audio.gst_pipeline import GstAudioPipeline


class Receiver:
    """
    High-level receiver abstraction.
    """

    def __init__(self, pipeline: GstAudioPipeline):

        self._pipeline = pipeline

    def start(self):

        self._pipeline.start()

    def stop(self):

        self._pipeline.stop()

    @property
    def volume(self) -> float:

        return self._pipeline.get_volume()

    @volume.setter
    def volume(self, value: float):

        self._pipeline.set_volume(value)