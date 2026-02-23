from fastapi import APIRouter, Depends, HTTPException, status
from models.opc import InputOPC
from models.taskOPC import VariableWriteInput
from typing import Annotated
from models.user import UserByToken, Role
from models.generic import GenericDevice
from routers.auth import get_current_admin_or_editor_user
from routers.task import get_state
from models.task import Task, State,NameTask
from asyncua import Client, ua
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from dotenv import load_dotenv
import os
from pathlib import Path
from beanie import PydanticObjectId
from routers.user import get_devices_names_by_user_id

opc_router = APIRouter(
    prefix="/opc",
    tags=["opc"],)


env_path = Path(__file__).resolve().parent.parent / 'tasks' / '.env'

load_dotenv(dotenv_path=env_path)

OPCUA_IP_PORT = os.getenv('OPCUA_IP_PORT')

URL_ADMIN=os.getenv('URL_ADMIN')

URL_ADMIN = URL_ADMIN.replace("{OPCUA_IP_PORT}", OPCUA_IP_PORT)

BASE_DIR = Path(__file__).resolve().parent.parent 

CERT = BASE_DIR / "tasks" / os.getenv('CERT')
PRIVATE_KEY = BASE_DIR / "tasks" / os.getenv('PRIVATE_KEY')
CLIENT_CERT = BASE_DIR / "tasks" / os.getenv('CLIENT_CERT')

# Server application URI
CLIENT_APP_URI= os.getenv('CLIENT_APP_URI')


USERNAME = os.getenv('USERNAME_OPC_ADMIN')
PASSWORD = os.getenv('PASSWORD_OPC_ADMIN')

URI = os.getenv('URI')

@opc_router.post("/write-value/{user_id}", status_code=status.HTTP_200_OK)
async def write_variable(user_id: PydanticObjectId, variable_input: VariableWriteInput, editor_user: Annotated[UserByToken, Depends(get_current_admin_or_editor_user)]):
    
    if editor_user.role != Role.admin and user_id != editor_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para consultar estos datos")
    
    user_devices_names = await get_devices_names_by_user_id(user_id=user_id)

    if variable_input.nameGenericDevice not in user_devices_names:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="El usuario no puede modificar variables de ese dispositivo")

    generic_device = await GenericDevice.by_name(variable_input.nameGenericDevice)

    if generic_device is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No existe el dispositivo")
    
    variable_atributes = await generic_device.find_variable_atributes_by_name(variable_input.nameVariable)

    if variable_atributes.writable == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La variable es de solo lectura")
    
    
    task = await Task.by_name(variable_input.deviceType)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La tarea '{variable_input.deviceType}' no existe")
    

    state = await get_state(task=task)

    if state != State.running:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El servicio '{variable_input.deviceType}' no se encuentra activo")
    
    taskOPC = await Task.by_name(NameTask.serverOPC)

    if not taskOPC:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El servidor OPC no existe actualmente")
    
    stateOPC = await get_state(task=taskOPC)

    if stateOPC != State.running:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El servidor OPC no se encuentra activo")
            
            
    try:
        client_opc = Client(URL_ADMIN, timeout=2)
        client_opc.application_uri = CLIENT_APP_URI
        await client_opc.set_security(
            SecurityPolicyBasic256Sha256,
            certificate=str(CLIENT_CERT),
            private_key=str(PRIVATE_KEY),
            server_certificate=str(CERT),
            mode=ua.MessageSecurityMode.SignAndEncrypt
        )
        client_opc.set_user(USERNAME)
        client_opc.set_password(PASSWORD)
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"OPC client creation failed: {e}")
    
    try:
        await client_opc.connect()
        nsidx = await client_opc.get_namespace_index(URI)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Connection to the OPC server failed")
    


    if variable_atributes.min_value is not None and variable_atributes.max_value is not None:
        if variable_input.value < variable_atributes.min_value or variable_input.value > variable_atributes.max_value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El valor se encuentra fuera de rango")
        
    value = variable_input.value
    if variable_atributes.scaling is not None:
        value = value / variable_atributes.scaling

    value_type = variable_atributes.type

    value = round(value, variable_atributes.decimals)
        
    try:

        variable_opc = client_opc.get_node(f"ns={nsidx};s={variable_input.nameGenericDevice}-{variable_input.nameVariable}")

        if(isinstance(value, float)):  
            if(value_type == InputOPC.int64 or value_type == InputOPC.uint64 or value_type == InputOPC.float64):
                await variable_opc.write_value(value, varianttype=ua.VariantType.Double)
            else:
                await variable_opc.write_value(value, varianttype=ua.VariantType.Float)
        else:
            if(value_type == InputOPC.int16):
                await variable_opc.write_value(value, varianttype=ua.VariantType.Int16)
            elif(value_type == InputOPC.uint16):
                await variable_opc.write_value(value, varianttype=ua.VariantType.UInt16)
            elif(value_type == InputOPC.int32):
                await variable_opc.write_value(value, varianttype=ua.VariantType.Int32)
            elif(value_type == InputOPC.uint32):
                await variable_opc.write_value(value, varianttype=ua.VariantType.UInt32)
            elif(value_type == InputOPC.int64):
                await variable_opc.write_value(value, varianttype=ua.VariantType.Int64)
            elif(value_type == InputOPC.uint64):
                await variable_opc.write_value(value, varianttype=ua.VariantType.UInt64)


    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La escritura del nuevo valor ha fallado")
    

    return {"message": f"Value modified successfully"}