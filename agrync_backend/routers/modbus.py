from fastapi import APIRouter, Depends, HTTPException, status,UploadFile, Body
from fastapi.responses import FileResponse
import json
from models.modbus import ModbusDevice,  DeviceInput, SlaveInput, VariableInput, VariableUpdate, SlaveUpdate, DeviceUpdate, VariableCreate, SlaveCreate, DeviceCreate, DevicesResponseList, DevicesList, SlavesList, SlavesResponseList, VariablesResponseList, VariablesList, DeviceSelect, DeviceSlaveSelect
from models.user import User, UserByToken
from models.generic import GenericDevice, LastVariable, HistoricalVariable, DeviceType, VariableAtributes
from beanie import  PydanticObjectId
from utils.datetime import time_at
from pydantic import ValidationError
import asyncio
from typing import Any
from pathlib import Path
from models.filters import FiltersPayload, FilterMode
from pymongo import DESCENDING, ASCENDING
from beanie.operators import And, RegEx, Or
from typing import Annotated
from routers.auth import get_current_admin_user

modbus_router = APIRouter(
    prefix="/modbus",
    tags=["modbus"],)






 

async def read_json(file: UploadFile) -> list[dict]:
    content = await file.read()
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, json.loads, content)
    return data

def validate_devices(data: list[dict]) -> list[DeviceInput]:
    return [DeviceInput(**device_data) for device_data in data]


def has_variable_changed_file(variable: VariableCreate, new_data: VariableInput, data_dump: dict[str, Any]) -> bool:
    return (
        ("interval" in data_dump and variable.interval != new_data.interval) or
        ("writable" in data_dump and variable.writable != new_data.writable) or
        ("min_value" in data_dump and variable.min_value != new_data.min_value) or
        ("max_value" in data_dump and variable.max_value != new_data.max_value) or
        ("unit" in data_dump and variable.unit != new_data.unit)
    )


def has_variable_changed_update(variable: VariableCreate, new_data: VariableUpdate, data_dump: dict[str, Any]) -> bool:
    return (
        (new_data.interval is not None and variable.interval != new_data.interval) or
        (new_data.writable is not None and variable.writable != new_data.writable) or
        ("min_value" in data_dump and variable.min_value != new_data.min_value) or
        ("max_value" in data_dump and variable.max_value != new_data.max_value) or
        ("unit" in data_dump and variable.unit != new_data.unit)
    )




async def process_devices(devices: list[DeviceInput], time_now):
    for device_data in devices:

            device_name_mod = device_data.name

            device = await ModbusDevice.by_ip(device_data.ip)

            #genericalDevice = await GenericDevice.by_name(device_name_mod)

            #device_no_exist = False

            #fetched_slaves = None

            device_changed = False
            device_created = False

            if device:

                if device.name != device_name_mod:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"No concuerdan IP ({device_data.ip}) y nombre de dispositivo ({device_name_mod})")
                #device.updatedAt = time_now
                #genericalDevice.updatedAt = time_now


                #fetched_slaves = await device.fetch_slaves()
                    


            else:


                if await ModbusDevice.check_by_name(device_name_mod):
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El nombre del dispositivo ya existe ({device_name_mod}), pero la IP ({device_data.ip}) no concuerda")
                else:
                    device = ModbusDevice(
                        name=device_name_mod,
                        ip=device_data.ip,
                        slaves=[]
                    )

                    device_created = True
                #device_no_exist = True

                #genericDevice = GenericDevice(name=device_name_mod, type=DeviceType.modbus)

            
            slave_list: list[SlaveCreate] = []
            slave_names_set = set()
            slave_ids_set = set()

            for slave_data in device_data.slaves:

                full_name_slave = device_data.name+"-"+slave_data.name
                
                #slave = await ModbusSlave.by_name(full_name_slave)
               
                slave = await device.find_slave_by_name(slave_data.name)

                #genericDevice = None
                #fetched_variables = None

                slave_changed = False
                slave_created = False

                if slave:
                    if slave.slave_id != slave_data.slave_id:    
                        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"No concuerdan id y nombre de esclavo: id -> {slave_data.slave_id}, name -> {slave_data.name}")
                    #slave.updatedAt = time_now

                    genericDevice = await GenericDevice.by_name(name=full_name_slave)

                    if genericDevice is None:
                        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"No se ha encontrado la pareja Dispositivo-Esclavo en el conjunto de dispositivos global")

                    #fetched_variables = await slave.fetch_variables()

                else:

                    if await device.check_slave_by_slave_id(slave_data.slave_id):
                        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El id ({slave_data.slave_id}) del esclavo ya existe para el dispositivo {device_data.name}")

                    

                    if slave_data.name in slave_names_set:
                        raise HTTPException(status_code=422, detail=f"Nombre de esclavo duplicado en el archivo: {slave_data.name}")

                    if slave_data.slave_id in slave_ids_set:
                        raise HTTPException(status_code=422, detail=f"Slave id duplicado en el archivo: {slave_data.slave_id}")

                    slave_names_set.add(slave_data.name)
                    slave_ids_set.add(slave_data.slave_id)

                    slave = SlaveCreate(
                        name=slave_data.name,
                        slave_id=slave_data.slave_id
                        #variables=[]
                    )

                    device_changed = True
                    slave_created = True

                    slave_list.append(slave)



                
                    genericDevice = GenericDevice(name=full_name_slave, type=DeviceType.modbus)




                variable_generic_list: list[VariableAtributes] = []
                variable_list: list[VariableCreate] = []
                variable_names_set = set()
                variable_address_set = set()

                for var_data in slave_data.variables:


                    full_name_var = device_data.name+"-"+slave_data.name+"-"+var_data.name

                    #var_type=var_data.type
                    var_data.address=var_data.address-1
                    #scaling=var_data.scaling
                    #decimals=var_data.decimals
                    #endian=var_data.endian
                    #interval=var_data.interval
                    #length=var_data.length
                    #writable= var_data.writable
                    #min_value=var_data.min_value
                    #max_value=var_data.max_value
                    #unit=var_data.unit


                    #variable = None

                    #variable = await ModbusVariable.by_name(full_name_var)
                    variable = await device.find_variable_by_name(name=var_data.name, name_slave=slave_data.name)

                    #lastVariable = await LastVariable.by_name(full_name_var)
                    #historicalVariable = await HistoricalVariable.by_name(full_name_var)


                    if variable:
                        if variable.address != var_data.address:    
                            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No concuerdan name y address de variable")
                        
                        data_dump = var_data.model_dump(exclude_unset=True)

                        has_changed = has_variable_changed_file(variable=variable, new_data=var_data, data_dump=data_dump)
                        
                        
                        if has_changed:
                            variable.updatedAt = time_now
                                 
                            slave_changed = True


                            variableAtributes = await genericDevice.find_variable_atributes_by_name(var_data.name)

                            if variableAtributes:

                                if "max_value" in data_dump:
                                    variableAtributes.max_value=var_data.max_value

                                    variable.max_value = var_data.max_value


                                if "min_value" in data_dump:
                                    variableAtributes.min_value=var_data.min_value

                                    variable.min_value = var_data.min_value

                                if "writable" in data_dump:
                                    variable.writable = var_data.writable

                                    variableAtributes.writable=var_data.writable

                                if "interval" in data_dump:
                                    variable.interval = var_data.interval

                                if "unit" in data_dump:
                                    variableAtributes.unit=var_data.unit

                                    variable.unit = var_data.unit


                    else:
                    
                        if await device.check_variable_by_address(address=var_data.address, name_slave=slave_data.name):
                            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El address envíado ({var_data.address + 1}) de la variable ya existe para el esclavo {slave_data.name}")

                        if var_data.type is None:
                            raise HTTPException(status_code=422, detail=f"Se tiene que proporcionar el tipo de una nueva variable: {var_data.name}")

                        if var_data.name in variable_names_set:
                            raise HTTPException(status_code=422, detail=f"Nombre de variable duplicado en el archivo: {var_data.name}")

                        if var_data.address in variable_address_set:
                            raise HTTPException(status_code=422, detail=f"Dirección de variable duplicada en el archivo: {var_data.address + 1}")

                        variable_names_set.add(var_data.name)
                        variable_address_set.add(var_data.address)


                        variable = VariableCreate(
                            name=var_data.name,
                            type=var_data.type,
                            address=var_data.address,
                            scaling=var_data.scaling,
                            decimals=var_data.decimals,
                            endian=var_data.endian,
                            interval=var_data.interval,
                            length=var_data.length,
                            writable= var_data.writable,
                            min_value=var_data.min_value,
                            max_value=var_data.max_value,
                            unit=var_data.unit
                        )

                        await LastVariable.create_last_variable(full_name_var)

                        #historical_variable = await HistoricalVariable.create_historical_variable(full_name_var)

                        #variable_save = await variable.create()

                        
                        variable_generic_list.append(VariableAtributes(max_value=var_data.max_value, min_value=var_data.min_value, 
                                                                       name=var_data.name, scaling=var_data.scaling, type=var_data.type, 
                                                                       unit=var_data.unit, writable=var_data.writable, decimals=var_data.decimals))

                        variable_list.append(variable)
                        slave_changed = True
                    
                    

                    
                if slave.variables is None:
                    slave.variables = []
                if variable_list:
                    slave.variables.extend(variable_list)

                if slave_changed:
                    if not slave_created:
                        slave.updatedAt = time_now
                    device_changed = True
            
                
                if genericDevice.variables is None:
                    genericDevice.variables = []
                if variable_generic_list:
                    genericDevice.variables.extend(variable_generic_list)
                
                await genericDevice.save()

                
            if device.slaves is None:
                device.slaves = []
            if slave_list:
                device.slaves.extend(slave_list)

            if device_changed:
                if not device_created:
                    device.updatedAt = time_now
                await device.save()


@modbus_router.post("/upload", status_code=status.HTTP_200_OK)
async def create_upload_file(file: UploadFile | None = None):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se ha recibido el archivo")
    else:

        if(file.content_type != "application/json"):
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Solo se admite archivos con formato JSON")
        

        try:
            #content = await file.read()
            #data = json.loads(content)
            data = await read_json(file)
        except json.JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El contenido no es un JSON válido")

        try:
            loop = asyncio.get_running_loop()
            devices = await loop.run_in_executor(None, validate_devices, data)
        except ValidationError as exc:
            errors = []
            for err in exc.errors():
                loc = ".".join(str(loc) for loc in err["loc"])
                errors.append({
                    "loc": loc,
                    "message": err["msg"],
                    "type": err["type"]
                })
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=errors)

        time_now = time_at()
        
        await process_devices(devices, time_now)

        return {"message": "Archivo recibido"}

 
'''
 Obtener una lista de los Dispositivos-Esclavos-Variables


@modbus_router.get("/list", status_code=status.HTTP_200_OK, response_model=list[ModbusDevice])
async def get_devices(skip: int = 0, limit: int = 10):
    devices = await ModbusDevice.find(fetch_links=True, skip=skip, limit=limit).to_list()
    return devices

'''

'''
 Enviar plantilla
'''

@modbus_router.get("/download-template", response_class=FileResponse)
async def download_json():
    file_path = Path("static/downloads/plantilla_modbus.json")
    if file_path.exists():
        return FileResponse(
            path=file_path,
            filename="plantilla_modbus.json",
            media_type="application/json"
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")










'''

 Endpoints Device

'''







@modbus_router.post('/devices/list', status_code=status.HTTP_200_OK, response_model=DevicesResponseList)
async def get_devices(
    current_admin: Annotated[UserByToken, Depends(get_current_admin_user)],
    filters_payload: Annotated[FiltersPayload, Body()]
):
    
    filters = filters_payload.columnFilters
    filterModes = filters_payload.columnFilterFns
    sorting = filters_payload.sorting
    globalFilter = filters_payload.globalFilter
    skip = filters_payload.pagination.pageIndex * filters_payload.pagination.pageSize
    limit = filters_payload.pagination.pageSize


    valid_fields = {
        'name', 'ip', 'createdAt', 'updatedAt'
    }

    partial_filters = []
    for col_filter in filters:
        field = col_filter.id  
        val = col_filter.value 
        if field not in valid_fields or not val:
            continue

        mode = filterModes.get(field, FilterMode.contains)  

        
        if mode == FilterMode.contains:
            partial_filters.append(RegEx(getattr(ModbusDevice, field), f".*{val}.*", options="i"))
        elif mode == FilterMode.startsWith:
            partial_filters.append(RegEx(getattr(ModbusDevice, field), f"^{val}", options="i"))
        elif mode == FilterMode.endsWith:
            partial_filters.append(RegEx(getattr(ModbusDevice, field), f"{val}$", options="i"))

    
    if partial_filters:
        query = And(*partial_filters)
    else:
        query = None

    
    if globalFilter:
        gf = globalFilter
        global_filters = [
            RegEx(getattr(ModbusDevice, field), f".*{gf}.*", options="i")
            for field in ['name', 'ip']
        ]
        if query:
            query = And(query, Or(*global_filters))  
        else:
            query = Or(*global_filters)  

    
    sort_params = []
    for sort in sorting:
        field = sort.get('id')  
        if field not in valid_fields:
            continue
        if sort.get('desc'):
            sort_params.append((getattr(ModbusDevice, field), DESCENDING))
        else:
            sort_params.append((getattr(ModbusDevice, field), ASCENDING))

    
    find_query = ModbusDevice.find(query) if query else ModbusDevice.find()
    if sort_params:
        find_query = find_query.sort(*sort_params)

    total = await find_query.count()
    devices = await find_query.skip(skip).limit(limit).to_list()

    
    devices_response = []
    for device in devices:
        data = device.model_dump() 
        devices_response.append(DevicesList(**data))

    return DevicesResponseList(data=devices_response, totalRowCount=total)













@modbus_router.post("/devices", status_code=status.HTTP_201_CREATED)
async def create_device(device_data: DeviceInput):

    if device_data is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Datos de dispositivo no enviados correctamente")

    device = await ModbusDevice.by_ip(str(device_data.ip))

    if device:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El dispositivo ya existe")
    
    else:
        device_exist = await ModbusDevice.check_by_name(device_data.name)

        if device_exist:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El dispositivo ya existe")
    
    
    device = ModbusDevice(ip=str(device_data.ip), name=device_data.name)
    await device.create()


    return {"message": "Dispositivo creado correctamente"}



def update_device_name(original: str, new_prefix: str) -> str:
    parts = original.split("-", 1)
    if len(parts) > 1 and len(parts) < 4:
        return new_prefix + "-" + parts[1]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error inesperado al intentar actualizar la parte del nombre correspondiente al dispositivo"
        )


@modbus_router.put("/devices/{device_db_id}", status_code=status.HTTP_200_OK)
async def update_device(device_db_id: PydanticObjectId, device_data: DeviceUpdate):

    if device_data is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Datos de dispositivo no enviados correctamente")

    device = await ModbusDevice.get(device_db_id)

    if device is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El dispositivo no existe")
    
    if (device_data.name is not None and device_data.name != device.name) or (device_data.ip is not None and device_data.ip != device.ip):

        if device_data.ip:
            device_ip_search = await ModbusDevice.by_ip(device_data.ip)

            if device_ip_search and device.id != device_ip_search.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La ip ya se utiliza")
        
        if device_data.name:
            device_name_search = await ModbusDevice.by_name(device_data.name)

            if device_name_search and device.id != device_name_search.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El nombre ya se utiliza")

        actual_time= time_at()

        if device_data.name is not None and device_data.name != device.name:

            if device.slaves:
                for slave in device.slaves:

                    full_name_slave = device.name + "-" + slave.name

                    users_found = await User.find_by_device_name(device_name=full_name_slave)

                    if users_found:
                        for user_found in users_found:
                            for i, device_name in enumerate(user_found.devices):
                                if device_name == full_name_slave:
                                    user_found.devices[i] = update_device_name(original=device_name, new_prefix=device_data.name)
                        
                            await user_found.replace()


                    generic_device = await GenericDevice.by_name(full_name_slave)

                    if generic_device:

                        generic_device.name = update_device_name(original=generic_device.name, new_prefix=device_data.name)

                        await generic_device.replace()

                    for variable in slave.variables:

                        full_name_variable = full_name_slave + "-" + variable.name

                        last_variable = await LastVariable.by_name(full_name_variable)

                        if last_variable:
                            last_variable.name = update_device_name(original=last_variable.name, new_prefix=device_data.name)
                            await last_variable.replace()

                        historical_variables = await HistoricalVariable.by_name(full_name_variable)

                        if historical_variables:
                            for historical_variable in historical_variables:
                                historical_variable.name = update_device_name(original=historical_variable.name, new_prefix=device_data.name)
                                await historical_variable.replace()

            device.name = device_data.name

        if device_data.ip is not None and device_data.ip != device.ip:
            device.ip = device_data.ip

        device.updatedAt = actual_time
        await device.replace()

        
        return {"message": "Dispositivo modificado correctamente"}
    
    return {"message": "No se realizaron cambios. Los datos ya son utilizados por el dispositivo"}



@modbus_router.delete("/devices/{device_db_id}", status_code=status.HTTP_200_OK)
async def delete_device(device_db_id: PydanticObjectId):
    device = await ModbusDevice.get(device_db_id)

    if device is not None:

        if device.slaves:
            for slave in device.slaves:
                #slave = await slave_link.fetch()

                full_name_slave = device.name + "-" + slave.name

                generic_device = await GenericDevice.by_name(full_name_slave)

                if generic_device:
                    await GenericDevice.delete(generic_device)
        
                if slave.variables:
                    for variable in slave.variables:
                        #variable = await var_link.fetch()

                        full_name_variable = full_name_slave + "-" + variable.name

                        last_variable = await LastVariable.by_name(full_name_variable)
                        historical_variables = await HistoricalVariable.by_name(full_name_variable)


                        if last_variable:
                            await LastVariable.delete(last_variable)

                        if historical_variables:
                            for historical_variable in historical_variables:
                                await HistoricalVariable.delete(historical_variable)

                        #await ModbusVariable.delete(variable)

                #await ModbusSlave.delete(slave)

        await ModbusDevice.delete(device)

        return {"message": "Dispositivo eliminado correctamente"}
    
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")






'''

 Endpoints Slave

'''



@modbus_router.post('/slaves/list', status_code=status.HTTP_200_OK, response_model=SlavesResponseList)
async def get_slaves(
    current_admin: Annotated[UserByToken, Depends(get_current_admin_user)],
    filters_payload: Annotated[FiltersPayload, Body()]
):
    filters = filters_payload.columnFilters
    filterModes = filters_payload.columnFilterFns
    sorting = filters_payload.sorting
    globalFilter = filters_payload.globalFilter
    skip = filters_payload.pagination.pageIndex * filters_payload.pagination.pageSize
    limit = filters_payload.pagination.pageSize

    valid_fields = {
        'name',         
        'slave_id',    
        'createdAt',   
        'updatedAt'    
    }

    numeric_fields = {'slave_id'}

    partial_filters = []
    for col_filter in filters:
        field = col_filter.id
        val = col_filter.value
        if field not in valid_fields or not val:
            continue

        mode = filterModes.get(field, FilterMode.contains)

        if field in numeric_fields:
            try:
                val_num = int(val)
            
                if mode == FilterMode.contains:
                    partial_filters.append({f"slaves.{field}": val_num})
                elif mode == FilterMode.startsWith:
                    partial_filters.append({f"slaves.{field}": {"$gte": val_num}})
                elif mode == FilterMode.endsWith:
                    partial_filters.append({f"slaves.{field}": {"$lte": val_num}})
            except ValueError:
                continue  

        else:

            if mode == FilterMode.contains:
                partial_filters.append(RegEx(f"slaves.{field}", f".*{val}.*", options="i"))
            elif mode == FilterMode.startsWith:
                partial_filters.append(RegEx(f"slaves.{field}", f"^{val}", options="i"))
            elif mode == FilterMode.endsWith:
                partial_filters.append(RegEx(f"slaves.{field}", f"{val}$", options="i"))

    if partial_filters:
        query = And(*partial_filters)
    else:
        query = None

    if globalFilter:
        gf = globalFilter
        global_filters = [
            RegEx(f"slaves.{field}", f".*{gf}.*", options="i")
            for field in ['name']
        ]
        if query:
            query = And(query, Or(*global_filters))
        else:
            query = Or(*global_filters)

    find_query = ModbusDevice.find(query) if query else ModbusDevice.find()
    devices = await find_query.to_list()

    slaves_response = []
    for device in devices:
        for slave in device.slaves or []:
            slaves_response.append(SlavesList(
                name=slave.name,
                slave_id=slave.slave_id,
                name_device=device.name,
                createdAt=slave.createdAt,
                updatedAt=slave.updatedAt,
                id=slave.id,
                id_device=device.id
            ))

    for sort in sorting:
        field = sort.get('id')
        if field not in valid_fields:
            continue
        reverse = sort.get('desc', False)

        slaves_response.sort(key=lambda s: getattr(s, field, None), reverse=reverse)

    total = len(slaves_response)
    paginated_slaves = slaves_response[skip:skip + limit]

    all_devices = await ModbusDevice.find_all().to_list()
    devices_available = [
        DeviceSelect(id=device.id, name=device.name)
        for device in all_devices
    ]

    return SlavesResponseList(data=paginated_slaves, totalRowCount=total, devicesAvailable=devices_available)












@modbus_router.post("/devices/{device_db_id}/slaves", status_code=status.HTTP_201_CREATED)
async def create_slave(device_db_id: PydanticObjectId, slave_data: SlaveInput):

    if slave_data is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Datos del esclavo no enviados correctamente")


    device = await ModbusDevice.get(device_db_id)

    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El dispositivo no existe")


    slave = await device.find_slave_by_name(slave_data.name)

    if slave:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El esclavo ya existe en ese dispositivo")
    
    else:
        
        if await device.check_slave_by_slave_id(slave_data.slave_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El esclavo ya existe en ese dispositivo")

    slave = SlaveCreate(slave_id=slave_data.slave_id, name=slave_data.name)

    full_name_slave = device.name+"-"+slave_data.name

    if device.slaves:
        device.slaves.append(slave)
    else:
        device.slaves = [slave]
    
    device.updatedAt = time_at()
    await device.replace()

    generic_device = GenericDevice(name = full_name_slave, type = DeviceType.modbus)
    await generic_device.create()

    return {"message": "Esclavo creado correctamente"}



def update_slave_name(original: str, new_slave: str) -> str:
    parts = original.split("-", 2)
    
    if len(parts) == 3:
        return f"{parts[0]}-{new_slave}-{parts[2]}"
    elif len(parts) == 2:
        return f"{parts[0]}-{new_slave}"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error inesperado al intentar actualizar la parte del nombre correspondiente al esclavo"
        )



@modbus_router.put("/devices/{device_db_id}/slaves/{slave_db_id}", status_code=status.HTTP_200_OK)
async def update_slave(device_db_id: PydanticObjectId, slave_db_id: PydanticObjectId, slave_data: SlaveUpdate):

    if slave_data is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Datos de esclavo no enviados correctamente")

    device = await ModbusDevice.get(device_db_id)

    if device is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El dispositivo no existe")
    
    slave_found = await device.find_slave_by_id(slave_db_id)

    if slave_found is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El esclavo no existe")

    if (slave_data.name is not None and slave_data.name != slave_found.name) or (slave_data.slave_id is not None and slave_data.slave_id != slave_found.slave_id):

        if slave_data.slave_id:
            slave_slaveId_search = await device.find_slave_by_slave_id(slave_data.slave_id)

            if slave_slaveId_search and slave_found.id != slave_slaveId_search.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El Id de esclavo ya se utiliza")
        
        if slave_data.name:
            slave_name_search = await device.find_slave_by_name(slave_data.name)

            if slave_name_search and slave_found.id != slave_name_search.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El nombre ya se utiliza")

        actual_time= time_at()

        if slave_data.name is not None and slave_data.name != slave_found.name:

            full_name_slave = device.name + "-" + slave_found.name

            users_found = await User.find_by_device_name(device_name=full_name_slave)

            if users_found:
                for user_found in users_found:
                    for i, device_name in enumerate(user_found.devices):
                        if device_name == full_name_slave:
                            user_found.devices[i] = update_slave_name(original=device_name, new_slave=slave_data.name)
                    
                    await user_found.replace()

            generic_device = await GenericDevice.by_name(full_name_slave)

            if generic_device:

                generic_device.name = update_slave_name(original=generic_device.name, new_slave=slave_data.name)

                await generic_device.replace()

            if slave_found.variables:
                for variable in slave_found.variables:

                    full_name_variable = full_name_slave + "-" + variable.name

                    last_variable = await LastVariable.by_name(full_name_variable)

                    if last_variable:
                        last_variable.name = update_slave_name(original=last_variable.name, new_slave=slave_data.name)
                        await last_variable.replace()

                    historical_variables = await HistoricalVariable.by_name(full_name_variable)

                    if historical_variables:
                        for historical_variable in historical_variables:
                            historical_variable.name = update_slave_name(original=historical_variable.name, new_slave=slave_data.name)
                            await historical_variable.replace()

            slave_found.name = slave_data.name

        if slave_data.slave_id is not None and slave_data.slave_id != slave_found.slave_id:
            slave_found.slave_id = slave_data.slave_id


        slave_found.updatedAt = actual_time
        device.updatedAt = actual_time
        await device.replace()

        
        return {"message": "Esclavo modificado correctamente"}
    
    return {"message": "No se realizaron cambios. Los datos ya son utilizados por el esclavo"}


@modbus_router.delete("/devices/{device_db_id}/slaves/{slave_db_id}", status_code=status.HTTP_200_OK)
async def delete_slave(device_db_id: PydanticObjectId, slave_db_id: PydanticObjectId):
    device = await ModbusDevice.get(device_db_id)

    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")

    slave_found = await device.find_slave_by_id(slave_db_id)
 
    if slave_found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Esclavo no encontrado en el dispositivo")

    full_name_slave = device.name + "-" + slave_found.name

    generic_device = await GenericDevice.by_name(full_name_slave)

    if generic_device:
        await GenericDevice.delete(generic_device)

    if slave_found.variables:
        for variable in slave_found.variables:

            full_name_variable = full_name_slave + "-" + variable.name

            last_variable = await LastVariable.by_name(full_name_variable)
            historical_variables = await HistoricalVariable.by_name(full_name_variable)

            if last_variable:
                await LastVariable.delete(last_variable)

            if historical_variables:
                for historical_variable in historical_variables:
                    await HistoricalVariable.delete(historical_variable)

    device.slaves.remove(slave_found)
    if not device.slaves: 
        device.slaves = None
    device.updatedAt = time_at()
    await device.replace()


    return {"message": "Esclavo eliminado correctamente"}


                










'''

 Endpoints Variable

'''



@modbus_router.post('/variables/list', status_code=status.HTTP_200_OK, response_model=VariablesResponseList)
async def get_variables(
    current_admin: Annotated[UserByToken, Depends(get_current_admin_user)],
    filters_payload: Annotated[FiltersPayload, Body()]
):
    filters = filters_payload.columnFilters
    filterModes = filters_payload.columnFilterFns
    sorting = filters_payload.sorting
    globalFilter = filters_payload.globalFilter
    skip = filters_payload.pagination.pageIndex * filters_payload.pagination.pageSize
    limit = filters_payload.pagination.pageSize

    valid_fields = {
        'name', 'type', 'address', 'scaling', 'decimals', 'endian', 'interval', 
        'length', 'writable', 'min_value', 'max_value', 'unit', 'createdAt', 'updatedAt'
    }

    numeric_fields = {'address', 'scaling', 'decimals', 'interval', 'length', 'min_value', 'max_value' }

    partial_filters = []
    for col_filter in filters:
        field = col_filter.id
        val = col_filter.value
        if field not in valid_fields or not val:
            continue
        mode = filterModes.get(field, FilterMode.contains)


        if field in numeric_fields:
            try:
                val_num = int(val)
            
            except ValueError:
            
                try:
                    val_num = float(val)
                except ValueError:
                    continue
            
            if mode == FilterMode.contains:
                partial_filters.append({f"slaves.variables.{field}": val_num})
            elif mode == FilterMode.startsWith:
                partial_filters.append({f"slaves.variables.{field}": {"$gte": val_num}})
            elif mode == FilterMode.endsWith:
                partial_filters.append({f"slaves.variables.{field}": {"$lte": val_num}})

        else:

            if mode == FilterMode.contains:
                partial_filters.append(RegEx(f"slaves.variables.{field}", f".*{val}.*", options="i"))
            elif mode == FilterMode.startsWith:
                partial_filters.append(RegEx(f"slaves.variables.{field}", f"^{val}", options="i"))
            elif mode == FilterMode.endsWith:
                partial_filters.append(RegEx(f"slaves.variables.{field}", f"{val}$", options="i"))

    query = And(*partial_filters) if partial_filters else None

    if globalFilter:
        gf = globalFilter
        global_filters = [
            RegEx(f"slaves.variables.{field}", f".*{gf}.*", options="i")
            for field in ['name', 'type']
        ]
        if query:
            query = And(query, Or(*global_filters))
        else:
            query = Or(*global_filters)

    find_query = ModbusDevice.find(query) if query else ModbusDevice.find()
    devices = await find_query.to_list()

    variables_response = []
    for device in devices:
        for slave in device.slaves or []:
            for variable in slave.variables or []:
                variables_response.append(VariablesList(
                    name=variable.name,
                    name_device=device.name,
                    name_slave=slave.name,
                    type=variable.type,
                    address=variable.address,
                    scaling=variable.scaling,
                    decimals=variable.decimals,
                    endian=variable.endian,
                    interval=variable.interval,
                    length=variable.length,
                    writable=variable.writable,
                    min_value=variable.min_value,
                    max_value=variable.max_value,
                    unit=variable.unit,
                    createdAt=variable.createdAt,
                    updatedAt=variable.updatedAt,
                    id=variable.id,
                    id_db_slave=slave.id,
                    id_db_device=device.id
                ))

    for sort in sorting:
        field = sort.get('id')
        if field not in valid_fields:
            continue
        reverse = sort.get('desc', False)
        variables_response.sort(key=lambda v: getattr(v, field, None), reverse=reverse)

    total = len(variables_response)
    paginated_variables = variables_response[skip:skip + limit]

    all_devices = await ModbusDevice.find_all().to_list()

    devices_slaves_available = []
    for device in all_devices:
        for slave in device.slaves or []:
            devices_slaves_available.append(DeviceSlaveSelect(
                id_db_slave=slave.id,
                id_db_device=device.id,
                name_device=device.name,
                name_slave=slave.name
            ))

    return VariablesResponseList(
        data=paginated_variables,
        totalRowCount=total,
        devicesSlavesAvailable=devices_slaves_available
    )








@modbus_router.post("/devices/{device_db_id}/slaves/{slave_db_id}/variables", status_code=status.HTTP_201_CREATED)
async def create_variable(device_db_id: PydanticObjectId, slave_db_id: PydanticObjectId, variable_data: VariableInput):

    if variable_data is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Datos de la variable no enviados correctamente")

    device = await ModbusDevice.get(device_db_id)

    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El dispositivo no existe")

    slave_found = await device.find_slave_by_id(slave_db_id)

    if slave_found is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El esclavo no existe en ese dispositivo")
    
    else:

        variable = await device.find_variable_by_name(name=variable_data.name, name_slave=slave_found.name)

        variable_data.address = variable_data.address-1

        if variable:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La variable ya existe en ese esclavo-dispositivo")

        else:
        
            if await device.check_variable_by_address(address=variable_data.address, name_slave=slave_found.name):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La variable ya existe en ese esclavo-dispositivo")

            if variable_data.type is None:
                raise HTTPException(status_code=422, detail=f"Se tiene que proporcionar el tipo de una nueva variable")

    variable = VariableCreate(name=variable_data.name, type=variable_data.type, address=variable_data.address,
                          scaling=variable_data.scaling, decimals= variable_data.decimals, endian=variable_data.endian,
                          interval=variable_data.interval, length=variable_data.length, writable=variable_data.writable,
                          min_value=variable_data.min_value, max_value=variable_data.max_value, unit=variable_data.unit)

    if slave_found.variables:
        slave_found.variables.append(variable)
    else:
        slave_found.variables = [variable]

    actual_time = time_at()

    slave_found.updatedAt = actual_time

    full_name_slave = device.name+"-"+slave_found.name

    full_name_variable = full_name_slave + "-" + variable_data.name

    await LastVariable.create_last_variable(name=full_name_variable)


    generic_device_found = await GenericDevice.by_name(full_name_slave)

    if generic_device_found.variables:
        generic_device_found.variables.append(VariableAtributes(max_value=variable_data.max_value, min_value=variable_data.min_value, 
                                                                       name=variable_data.name, scaling=variable_data.scaling, type=variable_data.type, 
                                                                       unit=variable_data.unit, writable=variable_data.writable, decimals=variable_data.decimals))
    else:
        generic_device_found.variables = [VariableAtributes(max_value=variable_data.max_value, min_value=variable_data.min_value, 
                                                                       name=variable_data.name, scaling=variable_data.scaling, type=variable_data.type, 
                                                                       unit=variable_data.unit, writable=variable_data.writable, decimals=variable_data.decimals)]
    
    await generic_device_found.replace()

    device.updatedAt = actual_time
    await device.replace()

    return {"message": "Variable creada correctamente"}


def update_variable_name(original: str, new_variable: str) -> str:
    parts = original.split("-", 2)
    if len(parts) == 3:
        return f"{parts[0]}-{parts[1]}-{new_variable}"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error inesperado al intentar actualizar la parte del nombre correspondiente a la variable"
        )


@modbus_router.put("/devices/{device_db_id}/slaves/{slave_db_id}/variables/{variable_db_id}", status_code=status.HTTP_200_OK)
async def update_variable(device_db_id: PydanticObjectId, slave_db_id: PydanticObjectId, variable_db_id: PydanticObjectId, variable_data: VariableUpdate):

    if variable_data is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Datos de variable no enviados correctamente")

    data_dump = variable_data.model_dump(exclude_unset=True)

    device = await ModbusDevice.get(device_db_id)

    if device is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El dispositivo no existe")
    
    slave_found = await device.find_slave_by_id(slave_db_id)

    if slave_found is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El esclavo no existe")

    variable_found = await device.find_variable_by_slave_and_variable_id(slave=slave_found, variable_db_id=variable_db_id)

    if variable_found is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La variable no existe")

    if (variable_data.name is not None and variable_data.name != variable_found.name) or has_variable_changed_update(variable=variable_found, new_data=variable_data,data_dump= data_dump):

        if variable_data.name:
            variable_name_search = await device.find_variable_by_name(name_slave=slave_found.name, name=variable_data.name)

            if variable_name_search and variable_found.id != variable_name_search.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El nombre ya se utiliza")

        actual_time= time_at()

        full_name_slave = device.name+"-"+slave_found.name

        full_name_variable = full_name_slave + "-" + variable_found.name

        if variable_data.name is not None and variable_data.name != variable_found.name:

            last_variable = await LastVariable.by_name(full_name_variable)

            if last_variable:
                last_variable.name = update_variable_name(original=last_variable.name, new_variable=variable_data.name)
                await last_variable.replace()

            historical_variables = await HistoricalVariable.by_name(full_name_variable)

            if historical_variables:
                for historical_variable in historical_variables:
                    historical_variable.name = update_variable_name(original=historical_variable.name, new_variable=variable_data.name)
                    await historical_variable.replace()

        generic_device = await GenericDevice.by_name(full_name_slave)

        if generic_device:
            if generic_device.variables:
                atributes_variable = await generic_device.find_variable_atributes_by_name(variable_found.name)
                
                atributes_variable.name = variable_data.name
                variable_found.name = variable_data.name

                if "max_value" in data_dump:
                    atributes_variable.max_value = variable_data.max_value
                    variable_found.max_value = variable_data.max_value

                if "min_value" in data_dump:
                    atributes_variable.min_value = variable_data.min_value
                    variable_found.min_value = variable_data.min_value

                if "unit" in data_dump:
                    atributes_variable.unit = variable_data.unit
                    variable_found.unit = variable_data.unit

                if variable_data.writable is not None:
                    atributes_variable.writable = variable_data.writable
                    variable_found.writable = variable_data.writable

                await generic_device.replace()

        #if variable_data.name is not None:
        #    variable_found.name = variable_data.name

        if variable_data.interval is not None:
            variable_found.interval = variable_data.interval

        variable_found.updatedAt = actual_time
        slave_found.updatedAt = actual_time
        device.updatedAt = actual_time
        await device.replace()

        
        return {"message": "Variable modificada correctamente"}
    
    return {"message": "No se realizaron cambios. Los datos ya son utilizados por la variable"}







                
@modbus_router.delete("/devices/{device_db_id}/slaves/{slave_db_id}/variables/{variable_db_id}", status_code=status.HTTP_200_OK)
async def delete_variable(device_db_id: PydanticObjectId, slave_db_id: PydanticObjectId, variable_db_id: PydanticObjectId):
    device = await ModbusDevice.get(device_db_id)

    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    

    slave_found = await device.find_slave_by_id(slave_db_id)
    
 
    if slave_found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Esclavo no encontrado en el dispositivo")

    

    variable_found = await device.find_variable_by_slave_and_variable_id(slave=slave_found, variable_db_id=variable_db_id)


    if variable_found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variable no encontrada")

    full_name_slave = device.name+"-"+slave_found.name

    generic_device = await GenericDevice.by_name(full_name_slave)
        
    variable_atributes = await generic_device.find_variable_atributes_by_name(variable_found.name)
    if variable_atributes:
        generic_device.variables.remove(variable_atributes)
        if not generic_device.variables:
            generic_device.variables = None
        await generic_device.replace()

    full_name_variable = full_name_slave + "-" + variable_found.name

    last_variable = await LastVariable.by_name(full_name_variable)

    if last_variable:
        await last_variable.delete()

    historical_variables = await HistoricalVariable.by_name(full_name_variable)
        
    if historical_variables:
        for historical_variable in historical_variables:
            await HistoricalVariable.delete(historical_variable)

    slave_found.variables.remove(variable_found)
    if not slave_found.variables: 
        slave_found.variables = None

    actual_time = time_at()
    slave_found.updatedAt = actual_time
    device.updatedAt = actual_time
    await device.replace()

    return {"message": "Variable eliminada correctamente"}

        
    












#@modbus_router.delete("/{id}", status_code=status.HTTP_200_OK)
#async def create_upload_file(file: UploadFile | None = None):