from fastapi import APIRouter, status, HTTPException, Query, Depends
from routers.user import get_devices_names_by_user_id
from models.generic import GenericDevice, LastVariable, HistoricalVariable, HistoricalVariableOut, DevicesVariablesNamesInput, DevicesVariablesNamesOutput, DeviceWithVariablesResponse, VariableAtributes, ValueWithTimestamp
from beanie import PydanticObjectId
from beanie.operators import In
from datetime import datetime
from enum import Enum
from typing import Annotated
from pymongo import ASCENDING
from models.user import UserByToken
from routers.auth import get_current_user
from models.user import Role

generic_router = APIRouter(
    prefix="/generic",
    tags=["generic"],)




@generic_router.get('/{user_id}', status_code=status.HTTP_200_OK, response_model=list[DevicesVariablesNamesInput])
async def get_names_user_devices_variables(user_id: PydanticObjectId, current_user: Annotated[UserByToken, Depends(get_current_user)]):
    
    if current_user.role != Role.admin and user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para consultar estos datos")

    user_devices_names = await get_devices_names_by_user_id(user_id=user_id)

    matched_devices = await GenericDevice.find(In(GenericDevice.name, user_devices_names)).project(DevicesVariablesNamesOutput).to_list()

    return matched_devices


async def get_filtered_devices_by_variables_names(user_id: PydanticObjectId, devices_names: list[DevicesVariablesNamesInput]):

    user_devices = await get_devices_names_by_user_id(user_id)

    devices_with_variables: dict[str, dict[str, list[VariableAtributes]]] = {}

    for device_input in devices_names:

        if device_input.name not in user_devices:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uno o más dispositivos no están disponibles para el usuario")
        
        generic_device = await GenericDevice.by_name(device_input.name)
        if generic_device is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uno o más dispositivos no existen")


        for variable_name in device_input.variables_names:
            variable = await generic_device.find_variable_atributes_by_name(variable_name)
                
            if variable is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Una o más variables no están disponibles para el usuario"
                )

                
            if device_input.name not in devices_with_variables:
                devices_with_variables[device_input.name] = {
                    'type': generic_device.type,
                    'variables': []
                }
                    
            devices_with_variables[device_input.name]['variables'].append(variable)

    devices_with_variables_response = []

    for device_name, device_data in devices_with_variables.items():
        devices_with_variables_response.append(
            DeviceWithVariablesResponse(
                name=device_name, 
                type=device_data['type'],
                variables=device_data['variables']
            )
        )

    return devices_with_variables_response

    

@generic_router.post('/filter-variables/{user_id}', status_code=status.HTTP_200_OK, response_model=list[DeviceWithVariablesResponse])
async def get_filtered_devices_variables(user_id: PydanticObjectId, devices_names: list[DevicesVariablesNamesInput], current_user: Annotated[UserByToken, Depends(get_current_user)]):
    
    if current_user.role != Role.admin and user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para consultar estos datos")
    
    return await get_filtered_devices_by_variables_names(user_id= user_id, devices_names= devices_names)






async def validate_and_get_deviceVariable_name_for_user(user_id: PydanticObjectId, devices_names: list[DevicesVariablesNamesInput]) -> list[str]:
    """Validates that the devices and variables are available to the user"""

    user_devices = await get_devices_names_by_user_id(user_id)

    device_variable_names = []

    for device_input in devices_names:
        
        if device_input.name not in user_devices:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uno o más dispositivos no están disponibles para el usuario")
        
        generic_device = await GenericDevice.by_name(device_input.name)
        if generic_device is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uno o más dispositivos no existen")


        for variable_name in device_input.variables_names:
            variable = await generic_device.find_variable_atributes_by_name(variable_name)
                
            if variable is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Una o más variables no están disponibles para el usuario"
                )
            
            device_variable_names.append(device_input.name + "-" + variable_name)

    return device_variable_names


async def get_last_variables(device_variable_names: list[str]):

    last_values = []

    for device_variable_name in device_variable_names:
        last_value = await LastVariable.by_name(device_variable_name)

        if last_value is None:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se pudo obtener uno o más de los últimos valores"
                )

        last_values.append(last_value)

    return last_values

@generic_router.post("/last-values/{user_id}")
async def get_last_values(user_id: PydanticObjectId, devices_names: list[DevicesVariablesNamesInput], current_user: Annotated[UserByToken, Depends(get_current_user)]):

    if current_user.role != Role.admin and user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para consultar estos datos")

    device_variable_names = await validate_and_get_deviceVariable_name_for_user(user_id=user_id, devices_names=devices_names)

    return await get_last_variables(device_variable_names)

            


class Aggregation(str, Enum):
    without = "sin"
    hours = "horas"
    days = "dias"


def detect_decimal_places(value: float | int) -> int:
    """etects the number of decimal places in a value"""
    value_str = str(value)
    if '.' in value_str:
        return len(value_str.split('.')[1].rstrip('0'))
    return 0

async def get_historical_variables(device_names: list[str], start_date: datetime, end_date: datetime, aggregation: Aggregation) -> list[HistoricalVariableOut]:
    match_stage = {
        "$match": {
            "name": {"$in": device_names},
            "day": {"$gte": start_date, "$lte": end_date}
        }
    }

    unwind_stage = {"$unwind": "$values"}

    match_date_stage = {
        "$match": {
            "values.timestamp": {"$gte": start_date, "$lte": end_date}
        }
    }

    if aggregation == Aggregation.without:
        group_stage = {
            "$group": {
                "_id": {
                    "name": "$name",
                    "timestamp": "$values.timestamp"
                },
                "avg_value": {"$avg": "$values.value"},
                "sample_value": {"$last": "$values.value"}
            }
        }
    elif aggregation == Aggregation.hours:
        group_stage = {
            "$group": {
                "_id": {
                    "name": "$name",
                    "year": {"$year": "$values.timestamp"},
                    "month": {"$month": "$values.timestamp"},
                    "day": {"$dayOfMonth": "$values.timestamp"},
                    "hour": {"$hour": "$values.timestamp"},
                },
                "avg_value": {"$avg": "$values.value"},
                "sample_value": {"$last": "$values.value"}
            }
        }
    elif aggregation == Aggregation.days:
        group_stage = {
            "$group": {
                "_id": {
                    "name": "$name",
                    "year": {"$year": "$values.timestamp"},
                    "month": {"$month": "$values.timestamp"},
                    "day": {"$dayOfMonth": "$values.timestamp"},
                },
                "avg_value": {"$avg": "$values.value"},
                "sample_value": {"$last": "$values.value"}
            }
        }

    project_stage = {
        "$project": {
            "name": "$_id.name",
            "timestamp": {
                "$dateFromParts": {
                    "year": "$_id.year",
                    "month": "$_id.month",
                    "day": "$_id.day",
                    "hour": {"$ifNull": ["$_id.hour", 0]},
                    "minute": 0,
                    "second": 0
                }
            },
            "avg_value": 1,
            "sample_value": 1,
            "_id": 0
        }
    } if aggregation != Aggregation.without else {
        "$project": {
            "name": "$_id.name",
            "timestamp": "$_id.timestamp",
            "avg_value": 1,
            "sample_value": 1,
            "_id": 0
        }
    }

    sort_stage = {"$sort": {"timestamp": ASCENDING}}

    if aggregation == Aggregation.without:
        pipeline = [
            {"$match": {"name": {"$in": device_names}}},
            {"$unwind": "$values"},
            {"$match": {"values.timestamp": {"$gte": start_date, "$lte": end_date}}},
            group_stage,
            project_stage,
            sort_stage
        ]
    else:
        pipeline = [
            match_stage,
            unwind_stage,
            match_date_stage,
            group_stage,
            project_stage,
            sort_stage
        ]

    results = await HistoricalVariable.aggregate(pipeline).to_list()

    grouped = {}

    for item in results:
        name = item['name']
        timestamp = item['timestamp']
        average = item['avg_value']
        sample_value = item.get('sample_value', average)

        decimals = detect_decimal_places(sample_value)
        rounded_value = round(average, decimals)

        if name not in grouped:
            grouped[name] = []

        grouped[name].append(ValueWithTimestamp(timestamp=timestamp, value=rounded_value))

    output = []

    for name in grouped:
        output.append(HistoricalVariableOut(name=name, series=grouped[name]))

    return output



@generic_router.post('/historical-values/{user_id}', status_code=status.HTTP_200_OK, response_model=list[HistoricalVariableOut])
async def get_historical_values(user_id: PydanticObjectId, current_user: Annotated[UserByToken, Depends(get_current_user)], device_names: list[DevicesVariablesNamesInput], start_date: Annotated[datetime, Query()], end_date: Annotated[datetime, Query()], aggregation: Annotated[Aggregation, Query()] = Aggregation.without):
    
    if current_user.role != Role.admin and user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para consultar estos datos")

    device_variable_names = await validate_and_get_deviceVariable_name_for_user(user_id=user_id, devices_names=device_names)

    return await get_historical_variables(device_names=device_variable_names, start_date=start_date, end_date=end_date, aggregation=aggregation)



