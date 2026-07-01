import logging
import unittest

from intercom.shared.logger import create_logger


class LoggerTest(unittest.TestCase):
    def test_returns_intercom_named_logger(self) -> None:
        logger = create_logger()

        self.assertEqual(logger.name, "intercom")

    def test_does_not_duplicate_handlers_on_repeated_calls(self) -> None:
        first = create_logger()
        handler_count = len(first.handlers)

        second = create_logger()

        self.assertIs(first, second)
        self.assertEqual(len(second.handlers), handler_count)

    def test_default_level_is_info(self) -> None:
        logger = create_logger()

        self.assertEqual(logger.level, logging.INFO)


if __name__ == "__main__":
    unittest.main()
