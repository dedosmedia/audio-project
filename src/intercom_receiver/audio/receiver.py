from intercom_receiver.audio.gst_pipeline import GstAudioPipeline


class Receiver:
    """
    High-level audio receiver abstraction.
    No GStreamer exposed outside this class.
    """

    def __init__(self, config):

        self._pipeline = GstAudioPipeline(config)

    def start(self):

        self._pipeline.start()

    def stop(self):

        self._pipeline.stop()

    def set_volume(self, value: float):

        self._pipeline.set_volume(value)

    def get_volume(self) -> float:

        return self._pipeline.get_volume()