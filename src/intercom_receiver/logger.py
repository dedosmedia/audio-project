import logging


LOGGER_NAME = "intercom"


def create_logger() -> logging.Logger:

    logger = logging.getLogger(LOGGER_NAME)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    handler = logging.StreamHandler()

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = create_logger()