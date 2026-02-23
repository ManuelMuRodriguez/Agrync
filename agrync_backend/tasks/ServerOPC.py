import logging
import logging.config

logging.getLogger('pymodbus').setLevel(logging.ERROR)
logging.getLogger('asyncua').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)

import json
import asyncio
from asyncua import Server, ua
from asyncua.server.users import UserRole, User
from dotenv import load_dotenv
import os
import sys
import signal
import time
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Link
from models.modbus import ModbusDevice
#from models.opc import VariableShortView, SlaveShortView, DeviceShortView
from agrync_backend.models.generic import GenericDevice  #, GenericShortView
from asyncua.ua.uaerrors import BadNodeIdExists




BASE_DIR = Path(__file__).resolve().parent
 
load_dotenv()

LOG_CONFIG = str(BASE_DIR / os.getenv("LOG_CONFIG", "logging.conf"))

# Log configuration for the Modbus client and OPC server
logging.config.fileConfig(LOG_CONFIG)

LOG_OPC= os.getenv("LOG_OPC")




    # Create logger for the OPC server
logger = logging.getLogger(LOG_OPC)

for handler in logging.getLogger().handlers:
    if handler.formatter:
        handler.formatter.converter = time.gmtime


# IP and port used to build the OPC server URL
OPCUA_IP_PORT = os.getenv('OPCUA_IP_PORT')

# OPC server URL
URL=os.getenv('URL')

URL = URL.replace("{OPCUA_IP_PORT}", OPCUA_IP_PORT)

# Username and password for the server user and administrator
USERNAME = os.getenv('USERNAME_OPC')
PASSWORD = os.getenv('PASSWORD_OPC')
USERNAME_ADMIN= os.getenv('USERNAME_OPC_ADMIN')
PASSWORD_ADMIN= os.getenv('PASSWORD_OPC_ADMIN')

# Server URL
URI = os.getenv('URI')

CERTIFICATE = str(BASE_DIR /os.getenv('CERT'))
PRIVATE_KEY= str(BASE_DIR /os.getenv('PRIVATE_KEY'))


# Access credential handler for the OPC server
class CustomUserManager:
    def get_user(self, iserver, username=None, password=None, certificate=None):
        if username == USERNAME_ADMIN:
            if password == PASSWORD_ADMIN:
                return User(role=UserRole.Admin)
        elif username == USERNAME:
            if password == PASSWORD:
                return User(role=UserRole.User)
        return None


async def setup():
    try: 
        client = AsyncIOMotorClient("mongodb://mongodb:27017").agrync
        await init_beanie(
            database=client,
            document_models=[GenericDevice]
        )
    except Exception as exc:
        print(f"Database connection error: {exc}")
        logger.error(f"Database connection error: {exc}")
        sys.exit(1)



# Create OPC UA server instance
server = Server(user_manager = CustomUserManager())


#async def get_specific_variable(generic_device: GenericDevice, generic_variable: str):
#    if generic_device.type == "Modbus":
#        return await ModbusVariable.by_name(generic_variable)
#    else:
#        return None


async def create_nodes(device: GenericDevice, idx: int):

    if device.type == "Modbus":
        
        device_name, slave_name = device.name.split("-", 1)

        nodeID = f"ns={idx};s={device_name}"

        try:
            device_node = await server.nodes.objects.add_object(nodeID, device_name)
        except BadNodeIdExists:
            device_node = server.get_node(nodeID)
        
        full_name_slave = device_name+"-"+slave_name

        nodeID = f"ns={idx};s={full_name_slave}"

        slave_node = await device_node.add_object(nodeID, full_name_slave)
            
        if device.variables is not None:
            for variable in device.variables:

                #specific_variable = await get_specific_variable(device, name_variable)

                full_name_variable = full_name_slave + "-" + variable.name

                nodeID = f"ns={idx};s={full_name_variable}"

                # Create node for the variable
                if(variable.type == "Float64"):
                    variable_node = await slave_node.add_variable(nodeID, full_name_variable, val= 0.0, varianttype=ua.VariantType.Double)
                    #variable_node = await slave_node.add_variable(nodeID, variable.name, ua.DataValue(ua.Variant(0.0, ua.VariantType.Double), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                elif(variable.type == "Float32"):
                    #variable_node = await slave_node.add_variable(nodeID, variable.name, ua.DataValue(ua.Variant(0.0, ua.VariantType.Float), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                    variable_node = await slave_node.add_variable(nodeID, full_name_variable, val= 0.0, varianttype=ua.VariantType.Float)
                else:
                    if isinstance(variable.scaling, float):
                        if(variable.type == "Int64" or variable.type == "UInt64"):
                            variable_node = await slave_node.add_variable(nodeID, full_name_variable, val=0.0, varianttype=ua.VariantType.Double)
                            #variable_node = await slave_node.add_variable(nodeID, variable.name, ua.DataValue(ua.Variant(0.0, ua.VariantType.Double), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                        else:
                            variable_node = await slave_node.add_variable(nodeID, full_name_variable, val=0.0, varianttype=ua.VariantType.Float)
                            #variable_node = await slave_node.add_variable(nodeID, variable.name, ua.DataValue(ua.Variant(0.0, ua.VariantType.Float), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                    else:
                        if(variable.type == "Int16"):    
                            variable_node = await slave_node.add_variable(nodeID, full_name_variable, val= 0, varianttype=ua.VariantType.Int16)
                            #variable_node = await slave_node.add_variable(nodeID, variable.name, ua.DataValue(ua.Variant(0, ua.VariantType.Int16), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                        elif(variable.type == "UInt16"):
                            variable_node = await slave_node.add_variable(nodeID, full_name_variable, val= 0, varianttype=ua.VariantType.UInt16)
                            #variable_node = await slave_node.add_variable(nodeID, variable.name, ua.DataValue(ua.Variant(0, ua.VariantType.UInt16), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                        elif(variable.type == "Int32"):
                            variable_node = await slave_node.add_variable(nodeID, full_name_variable, val= 0, varianttype=ua.VariantType.Int32)
                            #variable_node = await slave_node.add_variable(nodeID, variable.name, ua.DataValue(ua.Variant(0, ua.VariantType.Int32), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                        elif(variable.type == "UInt32"):
                            #variable_node = await slave_node.add_variable(nodeID, variable.name, ua.DataValue(ua.Variant(0, ua.VariantType.UInt32), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                            variable_node = await slave_node.add_variable(nodeID, full_name_variable, val= 0, varianttype=ua.VariantType.UInt32)
                        elif(variable.type == "Int64"):
                            #variable_node = await slave_node.add_variable(nodeID, variable.name, ua.DataValue(ua.Variant(0, ua.VariantType.Int64), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                            variable_node = await slave_node.add_variable(nodeID, full_name_variable, val= 0, varianttype=ua.VariantType.Int64)
                        elif(variable.type == "UInt64"):
                            #variable_node = await slave_node.add_variable(nodeID, variable.name, ua.DataValue(ua.Variant(0, ua.VariantType.UInt64), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                            variable_node = await slave_node.add_variable(nodeID, full_name_variable, val= 0, varianttype=ua.VariantType.UInt64)
                
                    # Mark certain variables as writable
                    await variable_node.set_writable(variable.writable)
                    if(variable.writable == False):
                        await variable_node.set_read_only()
        else: 
            logger.error("No variables found in the database")
            print("No variables found in the database")
            sys.exit(2)

    else:
        logger.error("No device found in the database")
        print("No device found in the database")
        sys.exit(3)

 

# Start the OPC server
async def run_opc_server(devices: list[GenericDevice]) -> None:


    # Configure the OPC UA server
    await server.init()

    #Server URL
    server.set_endpoint(URL)

    # Set server security policy
    server.set_security_policy(
        [
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt
        ]
    )

    # Load the certificate and keys required for encrypted communication
    await server.load_certificate(str(CERTIFICATE)) 
    await server.load_private_key(str(PRIVATE_KEY))
    
    
    idx = await server.register_namespace(URI)
    

    # Create a node for each device, slave and its variables
    for device in devices:

        await create_nodes(device, idx)

    # Start the OPC UA server
    await server.start()
    print(f"OPC UA server started at: {URL}")
    logger.info(f"OPC UA server started at: {URL}")
    


def signal_handler(signal, frame):
    logger.info("Shutting down OPC server...")
    print("Shutting down OPC server...")
    sys.exit(0)





async def main():

    logger.info("Starting OPC server...")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await setup()

    # Load devices from the database
    try:
        #devices = await ModbusDevice.find(fetch_links=True).project(DeviceShortView).to_list()
        
        #devices = await GenericDevice.find(fetch_links=True).project(GenericShortView).to_list()

        devices = await GenericDevice.find().to_list()

        #for device in devices:
        #    for variable in device.variables:
        #        await variable.config_variable.fetch()

        #print(json.dumps(devices.pop().model_dump(), indent=4))

        if not devices:
            print("No devices found")
            sys.exit(0)

        # Start the server
        await run_opc_server(devices)

        while True:
            await asyncio.sleep(0.1)
    except Exception as exc:
        logger.warning(f"Possible error during server execution {exc}")
        print(f"Possible error during server execution {exc}")
        await server.stop()
    
    except RuntimeError as exc:
        logger.warning(f"Possible error during server execution {exc}")
        print(f"Possible error during server execution {exc}")
        await server.stop()


if __name__ == "__main__":

    asyncio.run(main())