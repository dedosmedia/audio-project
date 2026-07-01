"""YAML-backed configuration for the receiver and sender.

Values must never be hardcoded in application code: everything that can
change between deployments (device names, ports, volume) lives in
config/receiver.yaml and config/sender.yaml and is loaded through the
classmethods below.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml

from intercom.shared.constants import (
    DEFAULT_LATENCY_MS,
    DEFAULT_UDP_PORT,
    DEFAULT_VOLUME,
    OPUS_BITRATE_BPS,
)
from intercom.shared.exceptions import ConfigError

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_CONFIG_DIR_ENV = "INTERCOM_CONFIG_DIR"


def _config_dir() -> Path:
    override = os.environ.get(_CONFIG_DIR_ENV)
    return Path(override) if override else _PROJECT_ROOT / "config"


def _resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else _PROJECT_ROOT / path


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ConfigError(f"Configuration file is empty or malformed: {path}")

    return data


@dataclass(slots=True, frozen=True)
class ReceiverConfig:
    udp_port: int = DEFAULT_UDP_PORT
    audio_device: str = "hw:1,0"
    latency_ms: int = DEFAULT_LATENCY_MS
    default_volume: float = DEFAULT_VOLUME
    api_port: int = 8443
    api_ssl_certfile: Optional[Path] = None
    api_ssl_keyfile: Optional[Path] = None

    @classmethod
    def from_yaml(cls, path: Optional[Path] = None) -> "ReceiverConfig":
        path = path or _config_dir() / "receiver.yaml"
        data = _load_yaml(path)

        try:
            audio = data["audio"]
            network = data["network"]
            volume = data["volume"]

            certfile = network.get("ssl_certfile")
            keyfile = network.get("ssl_keyfile")

            return cls(
                udp_port=int(network["udp_port"]),
                audio_device=str(audio["device"]),
                latency_ms=int(audio["latency_ms"]),
                default_volume=float(volume["default"]),
                api_port=int(network.get("api_port", 8443)),
                api_ssl_certfile=_resolve_path(certfile) if certfile else None,
                api_ssl_keyfile=_resolve_path(keyfile) if keyfile else None,
            )
        except KeyError as exc:
            raise ConfigError(f"Missing key {exc} in {path}") from exc


@dataclass(slots=True, frozen=True)
class SenderConfig:
    receiver_host: str = "127.0.0.1"
    udp_port: int = DEFAULT_UDP_PORT
    audio_device: Optional[str] = None
    bitrate: int = OPUS_BITRATE_BPS

    @classmethod
    def from_yaml(cls, path: Optional[Path] = None) -> "SenderConfig":
        path = path or _config_dir() / "sender.yaml"
        data = _load_yaml(path)

        try:
            audio = data["audio"]
            network = data["network"]
            opus = data.get("opus", {})
            return cls(
                receiver_host=str(network["host"]),
                udp_port=int(network["udp_port"]),
                audio_device=audio.get("device") or None,
                bitrate=int(opus.get("bitrate", OPUS_BITRATE_BPS)),
            )
        except KeyError as exc:
            raise ConfigError(f"Missing key {exc} in {path}") from exc
