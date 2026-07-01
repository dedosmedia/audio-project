import tempfile
import unittest
from pathlib import Path

from intercom.shared.config import ReceiverConfig, SenderConfig
from intercom.shared.exceptions import ConfigError


class ReceiverConfigTest(unittest.TestCase):
    def test_loads_valid_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receiver.yaml"
            path.write_text(
                "audio:\n"
                "  device: hw:1,0\n"
                "  latency_ms: 20\n"
                "network:\n"
                "  udp_port: 5002\n"
                "volume:\n"
                "  default: 0.5\n"
            )

            config = ReceiverConfig.from_yaml(path)

            self.assertEqual(config.udp_port, 5002)
            self.assertEqual(config.audio_device, "hw:1,0")
            self.assertEqual(config.latency_ms, 20)
            self.assertEqual(config.default_volume, 0.5)

    def test_missing_file_raises_config_error(self) -> None:
        with self.assertRaises(ConfigError):
            ReceiverConfig.from_yaml(Path("/nonexistent/receiver.yaml"))

    def test_missing_key_raises_config_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receiver.yaml"
            path.write_text("audio:\n  device: hw:1,0\n")

            with self.assertRaises(ConfigError):
                ReceiverConfig.from_yaml(path)

    def test_malformed_yaml_raises_config_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receiver.yaml"
            path.write_text("- just\n- a\n- list\n")

            with self.assertRaises(ConfigError):
                ReceiverConfig.from_yaml(path)


class SenderConfigTest(unittest.TestCase):
    def test_loads_valid_yaml_with_default_device(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sender.yaml"
            path.write_text(
                "audio:\n"
                "  device: null\n"
                "network:\n"
                "  host: 192.168.1.50\n"
                "  udp_port: 5002\n"
                "opus:\n"
                "  bitrate: 32000\n"
            )

            config = SenderConfig.from_yaml(path)

            self.assertEqual(config.receiver_host, "192.168.1.50")
            self.assertEqual(config.udp_port, 5002)
            self.assertIsNone(config.audio_device)
            self.assertEqual(config.bitrate, 32000)

    def test_missing_opus_section_uses_default_bitrate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sender.yaml"
            path.write_text(
                "audio:\n  device: null\nnetwork:\n  host: 127.0.0.1\n  udp_port: 5002\n"
            )

            config = SenderConfig.from_yaml(path)

            self.assertEqual(config.bitrate, 32000)


if __name__ == "__main__":
    unittest.main()
