
from pydantic import BaseModel
from models.opc import TypeOPC
from agrync_backend.models.generic import DeviceType
from typing import Dict



class TimestampMetadata(BaseModel):
    type: str = "DateTime"
    value: str  


class Metadata(BaseModel):
    timestamp: TimestampMetadata


class Attribute(BaseModel):
    value: int | float | None
    type: TypeOPC
    metadata: Metadata


class DeviceResponse(BaseModel):
    id: str
    type: DeviceType
    attributes: Dict[str, Attribute]


class Item(BaseModel):
    full_name: str
    value: int | float | None
    date_time: str
    data_type: TypeOPC