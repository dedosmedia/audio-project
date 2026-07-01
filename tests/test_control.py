import unittest

from fastapi.testclient import TestClient

from intercom.receiver.api.app import create_app
from intercom.shared.config import ReceiverConfig
from intercom.shared.exceptions import ServiceError


class FakeReceiver:
    """Duck-types the Receiver interface the control routes rely on,
    without touching any real GStreamer pipeline."""

    def __init__(self) -> None:
        self._running = True
        self._volume = 0.5
        self._muted = False
        self.fail_next = False

    def is_running(self) -> bool:
        return self._running

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._muted = False
        self._volume = value

    @property
    def is_muted(self) -> bool:
        return self._muted

    def toggle_mute(self) -> None:
        self._muted = not self._muted

    def start(self) -> None:
        if self.fail_next:
            raise ServiceError("boom")
        self._running = True

    def stop(self) -> None:
        if self.fail_next:
            raise ServiceError("boom")
        self._running = False


class ControlRoutesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.receiver = FakeReceiver()
        app = create_app(self.receiver, ReceiverConfig())
        self.client = TestClient(app)

    def test_get_status(self) -> None:
        response = self.client.get("/status")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"running": True, "volume": 0.5, "muted": False}
        )

    def test_set_volume(self) -> None:
        response = self.client.post("/volume", json={"value": 1.2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["volume"], 1.2)
        self.assertEqual(self.receiver.volume, 1.2)

    def test_set_volume_out_of_range_is_rejected(self) -> None:
        response = self.client.post("/volume", json={"value": 5.0})

        self.assertEqual(response.status_code, 422)

    def test_setting_volume_clears_mute(self) -> None:
        self.receiver.toggle_mute()

        response = self.client.post("/volume", json={"value": 0.8})

        self.assertFalse(response.json()["muted"])

    def test_toggle_mute(self) -> None:
        first = self.client.post("/mute")
        self.assertTrue(first.json()["muted"])

        second = self.client.post("/mute")
        self.assertFalse(second.json()["muted"])

    def test_start_and_stop(self) -> None:
        stop_response = self.client.post("/stop")
        self.assertFalse(stop_response.json()["running"])

        start_response = self.client.post("/start")
        self.assertTrue(start_response.json()["running"])

    def test_start_failure_returns_500(self) -> None:
        self.receiver.fail_next = True

        response = self.client.post("/start")

        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
