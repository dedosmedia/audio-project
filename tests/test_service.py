import unittest

from intercom.shared.exceptions import ServiceError
from intercom.shared.service import Service


class FakeService(Service):
    def __init__(self, fail_start: bool = False, fail_stop: bool = False) -> None:
        super().__init__()
        self.fail_start = fail_start
        self.fail_stop = fail_stop
        self.start_calls = 0
        self.stop_calls = 0

    def _do_start(self) -> None:
        if self.fail_start:
            raise RuntimeError("boom")
        self.start_calls += 1

    def _do_stop(self) -> None:
        if self.fail_stop:
            raise RuntimeError("boom")
        self.stop_calls += 1


class ServiceLifecycleTest(unittest.TestCase):
    def test_starts_and_reports_running(self) -> None:
        service = FakeService()

        self.assertFalse(service.is_running())

        service.start()

        self.assertTrue(service.is_running())
        self.assertEqual(service.start_calls, 1)

    def test_double_start_is_idempotent(self) -> None:
        service = FakeService()

        service.start()
        service.start()

        self.assertEqual(service.start_calls, 1)

    def test_stop_without_start_is_idempotent(self) -> None:
        service = FakeService()

        service.stop()

        self.assertEqual(service.stop_calls, 0)
        self.assertFalse(service.is_running())

    def test_restart_stops_then_starts(self) -> None:
        service = FakeService()

        service.start()
        service.restart()

        self.assertEqual(service.start_calls, 2)
        self.assertEqual(service.stop_calls, 1)
        self.assertTrue(service.is_running())

    def test_start_failure_raises_service_error_and_stays_stopped(self) -> None:
        service = FakeService(fail_start=True)

        with self.assertRaises(ServiceError):
            service.start()

        self.assertFalse(service.is_running())

    def test_stop_failure_raises_service_error_and_stays_running(self) -> None:
        service = FakeService(fail_stop=True)

        service.start()

        with self.assertRaises(ServiceError):
            service.stop()

        self.assertTrue(service.is_running())


if __name__ == "__main__":
    unittest.main()
