
from dataclasses import dataclass


@dataclass(slots=True)
class ReceiverConfig:
    udp_port: int = 5002

    audio_device: str = "hw:1,0"

    latency_ms: int = 20

    default_volume: float = 0.50


config = ReceiverConfig()