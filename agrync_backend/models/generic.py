from pydantic import BaseModel
from beanie import Document, Indexed
from typing import Annotated, Optional
from datetime import datetime
from enum import Enum
from models.opc import InputOPC
from models.task import NameTask

class DeviceType(str, Enum):
    modbus = NameTask.modbus.value


class VariableAtributes(BaseModel):
    name: str
    type: InputOPC
    scaling: float | int | None = None
    writable: bool = False
    min_value: float | int | None = None
    max_value: float | int | None = None
    unit: str | None = None
    decimals: int






class OnlyGenericName(BaseModel):
    name: str

class DevicesVariablesNamesInput(OnlyGenericName):
    variables_names: list[str]

class DevicesVariablesNamesOutput(DevicesVariablesNamesInput):
    type: DeviceType

    class Settings:
        projection = {"name": 1, "type": 1, "variables_names": "$variables.name"}


class DeviceWithVariablesResponse(BaseModel):
    name: str
    type: DeviceType
    variables: list[VariableAtributes]



class DevicesNames(BaseModel):
    names: list[str]

class VariablesNames(BaseModel):
    names: list[str]






class ValueWithTimestamp(BaseModel):
    value: float | int | None
    timestamp: datetime


class LastVariable(Document):
    name: Annotated[str, Indexed(unique=True)]
    value: float | int | None = None
    timestamp: datetime | None = None
    #createdAt: datetime = Field(default_factory=time_at)
    #updatedAt: datetime = Field(default_factory=time_at)

    def __repr__(self) -> str:
        return f"<LastVariable {self.name}: {self.value}>"

    def __str__(self) -> str:
        return f"{self.name}: {self.value}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LastVariable):
            return self.name == other.name
        return False

    @classmethod
    async def by_name(cls, name: str) -> Optional["LastVariable"]:
        """Get a generical last variable by name."""
        return await cls.find_one(cls.name == name)

    '''
    @classmethod
    async def by_device_name(cls, device_name: str) -> list["LastVariable"]:
        """Get a list of generical last variable by device name."""
        regex_pattern = f"^{re.escape(device_name)}-"
        return await cls.find({"name": {"$regex": regex_pattern}}).to_list()
    
    @classmethod
    async def by_slave_name(cls, device_slave_name: str) -> list["LastVariable"]:
        """Get a list of generical last variables by slave name."""
        prefix = f"{re.escape(device_slave_name)}-"
        regex_pattern = f"^{prefix}"
        return await cls.find({"name": {"$regex": regex_pattern}}).to_list()
    '''

    '''
    @classmethod
    async def by_device_name(cls, device_name: str) -> list["LastVariable"]:
        """Get a list of generical last variable by device or part of it name."""
        regex_pattern = f"^{device_name}-"
        return await cls.find({"name": {"$regex": regex_pattern}}).to_list()
    '''
    @classmethod
    async def create_last_variable(cls, name: str):

        new_last_variable = cls(
            name=name
        )

        await new_last_variable.create()
        return new_last_variable
    

    
class HistoricalVariableOut(BaseModel):
    name: str
    series: list[ValueWithTimestamp]
    


class HistoricalVariable(Document):
    name: Annotated[str, Indexed()]
    values: list[ValueWithTimestamp] | None = None
    day: Annotated[datetime, Indexed()]
    #createdAt: datetime = Field(default_factory=time_at)
    #updatedAt: datetime = Field(default_factory=time_at)

    def __repr__(self) -> str:
        return f"<HistoricalVariable {self.name}: {self.values}>"

    def __str__(self) -> str:
        return f"{self.name}: {self.values}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, HistoricalVariable):
            return self.name == other.name
        return False

    @classmethod
    async def by_name(cls, name: str) -> list["HistoricalVariable"]:
        """Get a set of generical historical variable by name."""
        variables = await cls.find(cls.name == name).to_list()
        return variables

    '''
    @classmethod
    async def by_device_name(cls, device_name: str) -> list["HistoricalVariable"]:
        """Get a list of generical historical variable by device name."""
        regex_pattern = f"^{device_name}-"
        return await cls.find({"name": {"$regex": regex_pattern}}).to_list()
    '''
        
    '''

    @classmethod
    async def by_device_name(cls, device_name: str) -> list["HistoricalVariable"]:
        """Get a list of generical historical variable by device name."""
        regex_pattern = f"^{re.escape(device_name)}-"
        return await cls.find({"name": {"$regex": regex_pattern}}).to_list()

    '''
        

    '''
    @classmethod
    async def create_historical_variable(cls, name: str):

        new_historical_variable = cls(
            name=name
        )

        await new_historical_variable.create()
        return new_historical_variable
    '''
    




'''
class ModbusVariableLink(BaseModel):
    #name: str
    config_variable: Link[ModbusVariable]
    last_variable: Link[LastVariable]
    historical_variable: Link[HistoricalVariable]


VariableLink = list[ModbusVariableLink]
'''

class GenericDevice(Document):
    name: Annotated[str, Indexed(unique=True)]
    type: DeviceType
    variables: list[VariableAtributes] | None = None
    #createdAt: datetime = Field(default_factory=time_at)
    #updatedAt: datetime = Field(default_factory=time_at)

    def __repr__(self) -> str:
        return f"<GenericDevice {self.name}: {self.type}>"

    def __str__(self) -> str:
        return f"{self.name}: {self.type}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GenericDevice):
            return self.name == other.name
        return False
    
    @classmethod
    async def by_name(cls, name: str) -> Optional["GenericDevice"]:
        """Get a generical device by name."""
        return await cls.find_one(cls.name == name)
    
    async def find_variable_atributes_by_name(self, name: str) -> Optional["VariableAtributes"]:
        """Search for a variable atributes by name and return it"""
        if self.variables:
            for variable in self.variables:
                if variable.name == name:
                    return variable
        return None


#class ModbusVariableLinkShortView(BaseModel):
    #name: str
#    config_variable: ModbusVariableShortView

#VariableLinkShortView = ModbusVariableLinkShortView

#class GenericShortView(BaseModel):
#    name: str
#    type: DeviceType
#    variables: list[VariableLinkShortView] | None