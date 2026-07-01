"""Shared constants for the RTP/Opus audio transport.

Sender and receiver pipelines must agree on these values, so they live
here instead of being duplicated (or hardcoded) on each side.
"""

RTP_PAYLOAD_TYPE_OPUS: int = 96
RTP_CLOCK_RATE_HZ: int = 48000
RTP_ENCODING_NAME: str = "OPUS"

AUDIO_CHANNELS: int = 1

OPUS_BITRATE_BPS: int = 32000

DEFAULT_UDP_PORT: int = 5002
DEFAULT_LATENCY_MS: int = 20
DEFAULT_VOLUME: float = 0.5
MIN_VOLUME: float = 0.0
MAX_VOLUME: float = 2.0
