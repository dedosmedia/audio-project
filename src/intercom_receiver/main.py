import signal
import sys
import time

from intercom_receiver.audio.gst_pipeline import GstAudioPipeline
from intercom_receiver.audio.receiver import Receiver
from intercom_receiver.config import config
from intercom_receiver.logger import logger


running = True


def shutdown_handler(signum, frame):

    global running

    logger.info("Shutdown requested")

    running = False


def main():

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    pipeline = GstAudioPipeline(config)

    receiver = Receiver(pipeline)

    receiver.start()

    logger.info("Receiver started")

    while running:
        time.sleep(0.2)

    receiver.stop()

    logger.info("Receiver stopped")

    sys.exit(0)


if __name__ == "__main__":
    main()