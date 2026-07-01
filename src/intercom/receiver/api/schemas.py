from pydantic import BaseModel, Field

from intercom.shared.constants import MAX_VOLUME, MIN_VOLUME


class VolumeRequest(BaseModel):
    value: float = Field(ge=MIN_VOLUME, le=MAX_VOLUME)


class StatusResponse(BaseModel):
    running: bool
    volume: float
    muted: bool
