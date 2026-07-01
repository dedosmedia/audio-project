"""REST control surface for the receiver: status, volume, mute, start/stop.

This module is the only place allowed to import FastAPI; receiver/audio
stays free of any HTTP concern per the project's architecture rules.
"""

from fastapi import APIRouter, HTTPException, Request

from intercom.receiver.api.schemas import StatusResponse, VolumeRequest
from intercom.receiver.audio.receiver import Receiver
from intercom.shared.exceptions import IntercomError

router = APIRouter()


def _get_receiver(request: Request) -> Receiver:
    return request.app.state.receiver


def _status(receiver: Receiver) -> StatusResponse:
    return StatusResponse(
        running=receiver.is_running(),
        volume=receiver.volume,
        muted=receiver.is_muted,
    )


@router.get("/status", response_model=StatusResponse)
def get_status(request: Request) -> StatusResponse:
    return _status(_get_receiver(request))


@router.post("/volume", response_model=StatusResponse)
def set_volume(body: VolumeRequest, request: Request) -> StatusResponse:
    receiver = _get_receiver(request)
    receiver.volume = body.value
    return _status(receiver)


@router.post("/mute", response_model=StatusResponse)
def toggle_mute(request: Request) -> StatusResponse:
    receiver = _get_receiver(request)
    receiver.toggle_mute()
    return _status(receiver)


@router.post("/start", response_model=StatusResponse)
def start_receiver(request: Request) -> StatusResponse:
    receiver = _get_receiver(request)
    try:
        receiver.start()
    except IntercomError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return _status(receiver)


@router.post("/stop", response_model=StatusResponse)
def stop_receiver(request: Request) -> StatusResponse:
    receiver = _get_receiver(request)
    try:
        receiver.stop()
    except IntercomError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return _status(receiver)
