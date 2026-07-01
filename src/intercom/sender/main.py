import signal
import sys
from types import FrameType
from typing import Optional

from gi.repository import GLib

from intercom.sender.audio.gst_pipeline import GstAudioPipeline
from intercom.sender.audio.sender import Sender
from intercom.shared.config import SenderConfig
from intercom.shared.exceptions import IntercomError
from intercom.shared.logger import logger


def main() -> None:
    loop = GLib.MainLoop()

    def shutdown_handler(signum: int, frame: Optional[FrameType]) -> None:
        logger.info("Shutdown requested")
        loop.quit()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    config = SenderConfig.from_yaml()

    pipeline = GstAudioPipeline(config)
    sender = Sender(pipeline)

    try:
        sender.start()
    except IntercomError:
        logger.exception("Sender failed to start")
        sys.exit(1)

    logger.info("Sender started -> %s:%s", config.receiver_host, config.udp_port)

    # GLib.MainLoop.run() drives the GStreamer bus dispatch: without it,
    # the bus signal watch registered in GstAudioPipeline never fires.
    loop.run()

    sender.stop()

    logger.info("Sender stopped")

    sys.exit(0)


if __name__ == "__main__":
    main()
