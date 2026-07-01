# Intercom Receiver

Audio receiver service for Raspberry Pi.

## Requirements

- Raspberry Pi OS Trixie
- Python 3.11+
- GStreamer 1.26+
- python3-gi
- python3-gst-1.0

## Create virtual environment

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

Install python dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
PYTHONPATH=src python -m intercom_receiver.main
```