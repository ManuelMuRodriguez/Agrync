from datetime import datetime
from fastapi import HTTPException, status
from enum import Enum
from typing import Annotated, Optional
import re
from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, field_validator, model_validator, Field
from ipaddress import IPv4Address
from utils.datetime import time_at
from models.opc import InputOPC

def depuration(text: str):
    cleaned_text = text.strip().replace(" ", "_")
    if re.search(r'[^a-zA-Z0-9_.\-]', cleaned_text):
        raise ValueError(f"Invalid text: '{text}' contains forbidden characters")
    return cleaned_text



class Endian(str, Enum):
    little = "Little"
    big = "Big"


class VariableUpdate(BaseModel):
    name: str | None = None
    #type: InputOPC | None = None
    #address: int | None = None
    #scaling: float | int | None = None
    #decimals: int | None = None
    #endian: Endian | None = None
    interval: int | None = None
    #length: int | None = None
    writable: bool | None = None
    min_value: float | int | None = None
    max_value: float | int | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def check_and_modify_model(self):
        
        if self.name:
            name = self.name

            depurated_name = depuration(name)

            if not depurated_name:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El nombre de una variable no puede estar vacío")

            if depurated_name.count('-') > 0:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El nombre de una variable no puede contener guiones ({depurated_name}) ('-')")

            self.name = depurated_name

        if self.interval is not None:
            if self.interval <= 1:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El valor de (interval) debe ser mayor que 1')

        min_value = self.min_value
        max_value = self.max_value

        if min_value is not None and max_value is not None and min_value > max_value:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El valor inferior del rango no puede ser mayor al superior")
        elif min_value is None and max_value is not None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Si se desea utilizar un rango deben especificarse ambos limites")
        elif max_value is None and min_value is not None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Si se desea utilizar un rango deben especificarse ambos limites")

        
        if self.unit is not None:
            strip_unit = self.unit.strip()
            if strip_unit:
                self.unit = strip_unit
            else:
                self.unit = None


        return self



class VariableInput(BaseModel):
    name: str
    type: InputOPC | None
    address: int
    scaling: float | int | None = None
    decimals: int = 0
    endian: Endian = Endian.big
    interval: int = 5
    length: int | None = None
    writable: bool = False
    min_value: float | int | None = None
    max_value: float | int | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def check_and_modify_model(self):
        
        name = self.name

        depurated_name = depuration(name)

        if not depurated_name:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El nombre de una variable no puede estar vacío")

        if depurated_name.count('-') > 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El nombre de una variable no puede contener guiones ({depurated_name}) ('-')")

        self.name = depurated_name



        if self.address <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El valor de (address) debe ser mayor que 0')

        #self.address = self.address - 1

        scaling = self.scaling

        if self.scaling is not None and scaling <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El valor de (scaling) debe ser mayor que 0')

        if self.decimals < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El valor de (decimals) debe ser mayor o igual que 0')

        if self.interval <= 1:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El valor de (interval) debe ser mayor que 1')

        length = self.length

        if length is not None and length <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El valor de (length) debe ser mayor que 0')


        min_value = self.min_value
        max_value = self.max_value

        if min_value is not None and max_value is not None and min_value > max_value:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El valor inferior del rango no puede ser mayor al superior")
        elif min_value is None and max_value is not None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Si se desea utilizar un rango deben especificarse ambos limites")
        elif max_value is None and min_value is not None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Si se desea utilizar un rango deben especificarse ambos limites")

        type = self.type

        if length is None:
            if type == InputOPC.uint16 or type == InputOPC.int16:
                self.length = 1  # 1 registro para UInt16/Int16
            elif type == InputOPC.uint32 or type == InputOPC.int32 or type == InputOPC.float32:
                self.length = 2  # 2 registros para UInt32/Int32/Float32
            elif type == InputOPC.uint64 or type == InputOPC.int64 or type == InputOPC.float64:
                self.length = 4  # 4 registros para UInt64/Int64/Float64
            else:
                self.length = 1  # Valor por defecto para otros tipos

        if self.unit is not None:
            strip_unit = self.unit.strip()
            if strip_unit:
                self.unit = strip_unit
            else:
                self.unit = None


        return self



class SlaveUpdate(BaseModel):
    name: str | None
    slave_id: int | None

    @field_validator('slave_id', mode="after")
    def check_id_non_negative_or_zero(cls, value: int | None):
        if value is not None:
            if value <= 0:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El valor de (slave_id) debe ser mayor que 0')
        return value

    @field_validator('name', mode="after")
    def set_name(cls, value: str | None):

        if value is None:
            return value

        depurated_name = depuration(value)

        if not depurated_name:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El nombre de un esclavo no puede estar vacío")
        
        if depurated_name.count('-') > 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El nombre de un esclavo no puede contener guiones ({depurated_name}) ('-')")

        return depurated_name



class SlaveInput(BaseModel):
    name: str
    slave_id: int
    variables: list[VariableInput] | None = None
    

    @field_validator('slave_id', mode="after")
    def check_id_non_negative_or_zero(cls, value: int):
        if value <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El valor de (slave_id) debe ser mayor que 0')
        return value

    @field_validator('name', mode="after")
    def set_name(cls, value: str):

        depurated_name = depuration(value)

        if not depurated_name:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El nombre de un esclavo no puede estar vacío")
        
        if depurated_name.count('-') > 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El nombre de un esclavo no puede contener guiones ({depurated_name}) ('-')")

        return depurated_name


class DeviceUpdate(BaseModel):
    name: str | None
    ip: str | None

    @field_validator('ip', mode="after")
    def validate_ip(cls, value: str | None):

        if value is None:
            return value

        try:
            check_ip = value
            IPv4Address(check_ip)
        except:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El valor de (ip) debe tener un formato correcto') 
        return value 

    @field_validator('name', mode="after")
    def set_name(cls, value: str | None):

        if value is None:
            return value

        depurated_name = depuration(value)

        if not depurated_name:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El nombre de un esclavo no puede estar vacío")
        
        if depurated_name.count('-') > 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El nombre de un esclavo no puede contener guiones ({depurated_name}) ('-')")

        return depurated_name

 
class DeviceInput(BaseModel):
    name: str
    ip: str
    slaves: list[SlaveInput] | None = None

    @field_validator('ip', mode="after")
    def validate_ip(cls, value: str):
        try:
            check_ip = value
            IPv4Address(check_ip)
        except:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El valor de (ip) debe tener un formato correcto')  
        return value  

    @field_validator("name", mode="after")
    def set_name(cls, value: str):

        depurated_name = depuration(value)

        if not depurated_name:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El nombre de un dispositivo no puede estar vacío")
        
        if depurated_name.count('-') > 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El nombre de un dispositivo no puede contener guiones ({depurated_name}) ('-')")

        return depurated_name













class VariableCreate(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    name: str
    type: InputOPC
    address: int
    scaling: float | int | None = None
    decimals: int = 0
    endian: Endian = Endian.big
    interval: int = 5
    length: int | None = None
    writable: bool = False
    min_value: float | int | None = None
    max_value: float | int | None = None
    unit: str | None = None
    createdAt: datetime = Field(default_factory=time_at)
    updatedAt: datetime = Field(default_factory=time_at)






class SlaveCreate(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    name: str
    slave_id: int
    variables: list[VariableCreate] | None = None
    createdAt: datetime = Field(default_factory=time_at)
    updatedAt: datetime = Field(default_factory=time_at)
    

 
class DeviceCreate(BaseModel):
    name: str
    ip: str
    slaves: list[SlaveCreate] | None = None

        

#class DeviceCreate(BaseModel):
#    name: str
#    ip: IPv4Address

#    @field_validator("name", mode="after")
#    def set_name(cls, value: str):

#        depurated_name = depuration(value)

#        if not depurated_name:
#            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El nombre de un dispositivo no puede estar vacío")
        
#        if depurated_name.count('-') > 0:
#            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El nombre de un dispositivo no puede contener guiones antes de procesarlo ({depurated_name}) ('-')")

#        return depurated_name

#class SlaveCreate(BaseModel):
#    device_db_id: PydanticObjectId
#    slave_id: int
#    name: str

#    @field_validator('slave_id', mode="after")
#    def check_id_non_negative_or_zero(cls, value: int):
#        if value <= 0:
#            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El valor de (slave_id) debe ser mayor que 0')
#        return value

#    @field_validator('name', mode="after")
#    def set_name(cls, value: str):

#        depurated_name = depuration(value)

#        if not depurated_name:
#            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El nombre de un esclavo no puede estar vacío")
        
#        if depurated_name.count('-') > 0:
#            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El nombre de un esclavo no puede contener guiones antes de procesarlo ({depurated_name}) ('-')")

#        return depurated_name

#class VariableCreate(VariableCreate):
#    device_db_id: PydanticObjectId
#    slave_db_id: PydanticObjectId












'''
class ModbusVariable(Document, VariableCreate):
    name: Annotated[str, Indexed(unique=True)]
    createdAt: datetime = Field(default_factory=time_at)
    updatedAt: datetime = Field(default_factory=time_at)
    
    def __repr__(self) -> str:
        return f"<ModbusVariable {self.name}: {self.address}>"

    def __str__(self) -> str:
        return f"{self.name}: {self.address}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ModbusVariable):
            return self.id == other.id
        return False

    @classmethod
    async def by_name(cls, name: str) -> Optional["ModbusVariable"]:
        """Get a variable by name."""
        return await cls.find_one(cls.name == name)
'''



'''

class ModbusSlave(Document, SlaveCreate):
    name: Annotated[str, Indexed(unique=True)]
    variables: list[Link[ModbusVariable]] | None = None
    createdAt: datetime = Field(default_factory=time_at)
    updatedAt: datetime = Field(default_factory=time_at)
    
    def __repr__(self) -> str:
        return f"<ModbusSlave {self.name}: {self.slave_id}>"

    def __str__(self) -> str:
        return f"{self.name}: {self.slave_id}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ModbusSlave):
            return self.id == other.id
        return False

    @classmethod
    async def by_name(cls, name: str) -> Optional["ModbusSlave"]:
        """Get a slave by name."""
        return await cls.find_one(cls.name == name)

    async def find_variable_by_name(self, name: str, fetched_variables: list["ModbusVariable"]) -> Optional["ModbusVariable"]:
        """Search for a variable by name in a list of fetched variables."""
        for variable in fetched_variables:
            if variable.name == name:
                return variable
        return None

    async def check_variable_by_address(self, address: int, fetched_variables: list["ModbusVariable"]) -> bool:
        """Check if a variable exists by address in a list of fetched variables."""
        for variable in fetched_variables:
            if variable.address == address:
                return True
        return False
    
    async def fetch_variables(self) -> list["ModbusVariable"]:
        """Fetches all variables associated with this slave and returns them as a list."""
        fetched_variables = []
        if self.variables:
            for variable_link in self.variables:
                variable = await variable_link.fetch()
                fetched_variables.append(variable)
        return fetched_variables

    async def find_variable_by_name_with_fetch(self, name: str) -> Optional["ModbusVariable"]:
        """Search for a variable by name and return it"""
        if self.variables:
            for variable_link in self.variables:
                variable = await variable_link.fetch()
                if variable.name == name:
                    return variable
        return None
    
    async def check_variable_by_address_with_fetch(self, address: int) -> bool:
        """Check if a variable exist by address"""
        if self.variables:
            for variable_link in self.variables:
                variable = await variable_link.fetch()
                if variable.address == address:
                    return True
        return False
'''


class ModbusDevice(Document, DeviceCreate):
    name: Annotated[str, Indexed(unique=True)]
    ip: Annotated[str, Indexed(unique=True)]
    slaves: list[SlaveCreate] | None = None
    createdAt: datetime = Field(default_factory=time_at)
    updatedAt: datetime = Field(default_factory=time_at)

    '''
    class Settings:
        indexes = [
            "slaves._id",               
            "slaves.variables._id",
            "slaves.name",
            "slaves.slave_id",
            "slaves.variables.address",
            "slaves.variables.name"    
        ]
    '''

    def __repr__(self) -> str:
        return f"<ModbusDevice {self.name}: {self.ip}>"

    def __str__(self) -> str:
        return f"{self.name}: {self.ip}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ModbusDevice):
            return self.ip == other.ip
        return False
    
    @classmethod
    async def by_ip(cls, ip: str) -> Optional["ModbusDevice"]:
        """Get a device by ip."""
        return await cls.find_one(cls.ip == ip)
    
    @classmethod
    async def by_name(cls, name: str) -> Optional["ModbusDevice"]:
        """Get a device by name."""
        return await cls.find_one(cls.name == name)
    
    @classmethod
    async def check_by_name(cls, name: str) -> bool:
        """Check if a device exist by name"""
        device = await cls.find_one(cls.name == name)  
        return device is not None
    

    async def find_slave_by_id(self, slave_db_id: str) -> Optional["SlaveCreate"]:
        """Find and return a slave by its db id."""
        if self.slaves:
            for slave in self.slaves:
                if slave.id == slave_db_id:
                    return slave  
        return None
    
    async def find_variable_by_slave_and_variable_id(self, slave: "SlaveCreate", variable_db_id: str) -> Optional["VariableCreate"]:
        """Find and return a variable by slave and variable id"""
    
        if slave and slave.variables:
            for variable in slave.variables:
                if variable.id == variable_db_id:
                    return variable
        return None

    '''
    @classmethod
    async def get_slave_by_ids(cls, device_db_id: PydanticObjectId, slave_db_id: PydanticObjectId) -> Optional["SlaveCreate"]:
        
        device = await cls.get(device_db_id)

        if device is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
        
        if device.slaves:
            for slave in device.slaves:
                if slave.id == slave_db_id:
                    return slave
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el esclavo en el dispositivo")

    @classmethod
    async def get_variable_by_ids(cls, device_db_id: PydanticObjectId, slave_db_id: PydanticObjectId, variable_db_id: PydanticObjectId) -> Optional["SlaveCreate"]:
        
        device = await cls.get(device_db_id)
        
        if device:
            for slave in device.slaves:
                if slave.id == slave_db_id:
                    for variable in slave.variables:
                        if variable.id == variable_db_id:
                            return variable
                    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado la variable en el dispositivo-esclavo")
    '''

    # Slave
    async def find_slave_by_name(self, name: str) -> Optional["SlaveCreate"]:
        """Search for a slave by name in the provided list and return it"""

        if self.slaves:
            for slave in self.slaves:
                if slave.name == name:
                    return slave
        return None
    
    async def find_slave_by_slave_id(self, slave_id: int) -> Optional["SlaveCreate"]:
        """Search for a slave by slave_id in the provided list and return it"""

        if self.slaves:
            for slave in self.slaves:
                if slave.slave_id == slave_id:
                    return slave
        return None

    async def check_slave_by_slave_id(self, slave_id: int) -> bool:
        """Check if a slave exists by slave_id in the provided list"""
        if self.slaves:
            for slave in self.slaves:
                if slave.slave_id == slave_id:
                    return True
        return False
    

    # Variable
    async def find_variable_by_name(self, name: str, name_slave: str) -> Optional["VariableCreate"]:
        """Search for a variable by name and return it"""
        if self.slaves:
            for slave in self.slaves:
                if slave.name == name_slave:
                    if slave.variables:
                        for variable in slave.variables:
                            if variable.name == name:
                                return variable
        return None
    
    async def check_variable_by_address(self, address: int, name_slave: str) -> bool:
        """Check if a variable exist by address"""
        if self.slaves:
            for slave in self.slaves:
                if slave.name == name_slave:
                    if slave.variables:
                        for variable in slave.variables:
                            if variable.address == address:
                                return True
        return False




    '''
    async def fetch_slaves(self) -> list["SlaveCreate"]:
        """Fetches all slaves associated with this device and returns them as a list."""
        fetched_slaves = []
        if self.slaves:
            for slave_link in self.slaves:
                slave = await slave_link.fetch()
                fetched_slaves.append(slave)
        return fetched_slaves
    
    
    async def find_slave_by_name_with_fetch(self, name: str) -> Optional["SlaveCreate"]:
        """Search for a slave by name and return it"""
        if self.slaves:
            for slave in self.slaves:
                if slave.name == name:
                    return slave
        return None
    
    async def check_slave_by_slave_id_with_fetch(self, slave_id: int) -> bool:
        """Check if a slave exist by slave_id"""
        if self.slaves:
            for slave in self.slaves:
                if slave.slave_id == slave_id:
                    return True
        return False
    '''



#class ModbusVariableShortView(BaseModel):
#    name: str
#    type: InputOPC
#    scaling: float | int | None
#    writable: bool





class VariableWithSlave(BaseModel):
    variable: VariableCreate
    slave_id: int
    full_name_variable: str
    #slave_name: str


class WritableNode(BaseModel):
    variable_name: str
    address: int

class VariableOPC(BaseModel):
    value: int | float | None
    type: InputOPC
    variable_name: str







class DevicesList(BaseModel):
    name: str
    ip: str
    createdAt: datetime
    updatedAt: datetime
    id: PydanticObjectId

class DevicesResponseList(BaseModel):
    data: list[DevicesList]
    totalRowCount: int



class DeviceSelect(BaseModel):
    id: PydanticObjectId 
    name: str

class SlavesList(BaseModel):
    name: str
    slave_id: int
    name_device: str
    createdAt: datetime
    updatedAt: datetime
    id: PydanticObjectId
    id_device: PydanticObjectId

class SlavesResponseList(BaseModel):
    data: list[SlavesList]
    totalRowCount: int
    devicesAvailable: list[DeviceSelect]




class DeviceSlaveSelect(BaseModel):
    id_db_device: PydanticObjectId 
    id_db_slave: PydanticObjectId 
    name_device: str
    name_slave: str


class VariablesList(BaseModel):
    name: str
    name_device: str
    name_slave: str
    type: InputOPC
    address: int
    scaling: float | int | None
    decimals: int
    endian: Endian
    interval: int | None
    length: int | None
    writable: bool
    min_value: float | int | None
    max_value: float | int | None
    unit: str | None
    createdAt: datetime
    updatedAt: datetime
    id: PydanticObjectId
    id_db_slave: PydanticObjectId
    id_db_device: PydanticObjectId

class VariablesResponseList(BaseModel):
    data: list[VariablesList]
    totalRowCount: int
    devicesSlavesAvailable: list[DeviceSlaveSelect]
