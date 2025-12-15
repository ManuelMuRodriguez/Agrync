from pydantic import BaseModel
from models.generic import DeviceType


class VariableWriteInput(BaseModel):
    nameVariable: str
    nameGenericDevice: str
    value: int | float
    deviceType: DeviceType