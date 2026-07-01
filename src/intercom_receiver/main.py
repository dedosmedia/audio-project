from intercom_receiver.config import config
from intercom_receiver.logger import logger


def main():

    logger.info("Starting Intercom Receiver")

    logger.info("UDP Port: %d", config.udp_port)

    logger.info("Audio Device: %s", config.audio_device)

    logger.info("Latency: %d ms", config.latency_ms)

    logger.info("Default Volume: %.2f", config.default_volume)

    logger.info("Receiver initialization complete")


if __name__ == "__main__":
    main()