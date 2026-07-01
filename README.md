# Intercom

Network audio intercom: live voice from a Linux Mint PC (sender) to a
Raspberry Pi (receiver) over Opus/RTP/UDP.

## Requirements

- Python 3.11+
- GStreamer 1.20+ with the `opus`, `rtp`, `udp`, and `pipewire` plugins
- System packages: `python3-gi`, `gir1.2-gstreamer-1.0`, `gstreamer1.0-plugins-base`,
  `gstreamer1.0-plugins-good` (these provide PyGObject and GStreamer bindings;
  they are not installable via pip)

## Create virtual environment

PyGObject is pulled from the system packages above, so the venv must be
created with access to system site-packages:

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Both services load their settings from YAML in `config/`:

- `config/receiver.yaml` — audio device, jitter buffer latency, UDP port, default volume
- `config/sender.yaml` — receiver host/port, capture device, Opus bitrate

Set `INTERCOM_CONFIG_DIR` to point at a different config directory (e.g. for tests).

## Run the receiver (Raspberry Pi)

```bash
PYTHONPATH=src python -m intercom.receiver.main
```

## Run the sender (Linux Mint PC)

Edit `config/sender.yaml` and set `network.host` to the receiver's LAN IP
(it defaults to `127.0.0.1` for local loopback testing).

```bash
PYTHONPATH=src python -m intercom.sender.main
```
