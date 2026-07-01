import logging


def create_logger() -> logging.Logger:

    logger = logging.getLogger("intercom")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        "%H:%M:%S",
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = create_logger()