"""FastAPI application factory for the receiver's REST/WebSocket layer.

Composed in receiver/main.py alongside the audio Service; never imported
by receiver/audio.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from intercom.receiver.api import control, mic_ingest
from intercom.receiver.audio.receiver import Receiver
from intercom.shared.config import ReceiverConfig

_STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app(receiver: Receiver, receiver_config: ReceiverConfig) -> FastAPI:
    app = FastAPI(title="Intercom Receiver API")

    app.state.receiver = receiver
    app.state.receiver_config = receiver_config

    app.include_router(control.router)
    app.include_router(mic_ingest.router)

    app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="static")

    return app
