from enum import Enum

class InputOPC(str, Enum):
    int16 = 'Int16'
    uint16 = 'UInt16'
    int32 = 'Int32'
    uint32 = 'UInt32'
    int64 = 'Int64'
    uint64 = 'UInt64'
    float32 = 'Float32'
    float64 = 'Float64'

class TypeOPC(str, Enum):
    int16 = 'Int16'
    uint16 = 'UInt16'
    int32 = 'Int32'
    uint32 = 'UInt32'
    int64 = 'Int64'
    uint64 = 'UInt64'
    float = 'Float'
    double = 'Double'

#class VariableShortView(BaseModel):
#    name: str
#    type: InputOPC
#    writable: bool
#    scaling: float | int | None

#class SlaveShortView(BaseModel):
#    name: str
#    variables: list[VariableShortView]



#class DeviceShortView(BaseModel):
#    name: str
#    slaves: list[SlaveShortView]
