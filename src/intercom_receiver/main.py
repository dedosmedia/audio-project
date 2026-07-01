import time

from intercom_receiver.config import config
from intercom_receiver.logger import logger
from intercom_receiver.audio.receiver import Receiver


def main():

    logger.info("Starting Intercom Receiver")

    receiver = Receiver(config)

    logger.info("Starting audio pipeline...")
    receiver.start()

    logger.info("Receiver is running (UDP port %d)", config.udp_port)
    logger.info("Press Ctrl+C to stop")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        logger.info("Stopping receiver...")

        receiver.stop()

        logger.info("Stopped cleanly")


if __name__ == "__main__":

    main()